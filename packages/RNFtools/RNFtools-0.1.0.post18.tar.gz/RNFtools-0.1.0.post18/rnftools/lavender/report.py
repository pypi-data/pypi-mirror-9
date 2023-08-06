import rnftools
import snakemake
import os


##############
##############
### REPORT ###
##############
##############
class Report:
	"""Class for an entire report."""

	def __init__(
		self,
		name,
		bam_dirs=[],
		allowed_delta=5,
		default_x_run=(0.00001,1.0),
		default_y_run=(60,100),
		default_pdf_size_cm=(10,10),
		default_svg_size_px=(640,640),
		keep_intermediate_files=False,
		compress_intermediate_files=True,
		default_x_axis="({m}+{w})/({M}+{m}+{w})",
		default_x_label="False positive rate in mapping {{/:Italic(#wrongly mapped reads / #mapped reads)}}",
		):
		"""

		:param name: Name of the report.
		:type  name: str
		:param bam_dirs: Directories with BAM files.
		:type  bam_dirs: list of str
		:param allowed_delta: Tolerance of difference between positions in assessing correct alignments (very important parameter!).
		:type  allowed_delta: int
		:param default_x_run: Range for x-axis in GnuPlot plots.
		:type  default_x_run: (float,float)
		:param default_y_run: Range for y-axis in GnuPlot plots.
		:type  default_y_run: (float,float)
		:param default_pdf_size_cm: Size of PDF page.
		:type  default_pdf_size_cm: (float,float)
		:param default_svg_size_px: Size of SVG picture.
		:type  default_svg_size_px: (int,int)

		"""

		rnftools.lavender.add_report(self)

		self.name = name
		self.report_dir = self.name

		self.default_x_run=self._load_x_run(default_x_run)
		self.default_y_run=self._load_y_run(default_y_run)
		self.default_pdf_size_cm=self._load_pdf_size_cm(default_pdf_size_cm)
		self.default_svg_size_px=self._load_svg_size_px(default_svg_size_px)
		self.default_x_label=default_x_label

		self.allowed_delta=int(allowed_delta)
		assert 0 <= allowed_delta

		self._html_fn = name+".html"
		self.panels = [
				rnftools.lavender.Panel(
					bam_dir=bam_dirs[i],
					panel_dir=os.path.join(self.report_dir,str(i)),
					report=self,
					name=str(i),
					keep_intermediate_files=keep_intermediate_files,
					compress_intermediate_files=compress_intermediate_files,
					default_x_axis=default_x_axis,
					default_x_label=default_x_label,
				)
				for i in range(len(bam_dirs))
			]

		rnftools.lavender.add_input(self._html_fn)

		# first graph
		self.add_graph(
			"({M}+{m}+{w}+{P}+{x})/{all}",
			title="Mapped reads in all reads",
			y_label="Mapped reads"
		)
		self.add_graph(
			"{M}/({M}+{m}+{w}+{P}+{x})",
			title="Correctly mapped reads in all mapped reads",
			y_label="Part of correctly mapped reads in all mapped reads",
		)

		self.add_graph(
			"{M}/({M}+{w}+{x}+{u}+{t}+{P})",
			title="Correctly mapped reads in all reads which should be mapped",
			y_label="Part of correctly mapped reads in reads which should be mapped",
		)

		self.add_graph(
			"({U}+{T})/({u}+{U}+{t}+{T})",
			title="Correctly unmapped reads in all unmapped reads",
			y_label="Part of correctly unmapped reads in all unmapped reads",
		)

		self.add_graph(
			"({U}+{T})/({U}+{T}+{m})",
			title="Correctly unmapped reads in all reads which should be unmapped",
			y_label="Part of correctly unmapped reads in reads which should be unmapped",
		)



	def add_graph(self,
				y,
				x_label=None,
				y_label="",
				title="",
				x_run=None,
				y_run=None,
				pdf_size_cm=None,
				svg_size_px=None,
				key_position="top left",
			):

		if x_run==None:
			x_run=self.default_x_run
		if y_run==None:
			y_run=self.default_y_run
		if pdf_size_cm==None:
			pdf_size_cm=self.default_pdf_size_cm
		if svg_size_px==None:
			svg_size_px=self.default_svg_size_px

		for panel in self.panels:
			x_run=self._load_x_run(x_run)
			y_run=self._load_y_run(y_run)
			pdf_size_cm=self._load_pdf_size_cm(pdf_size_cm)
			svg_size_px=self._load_svg_size_px(svg_size_px)
			panel.add_graph(
					y=y,
					x_run=x_run,
					y_run=y_run,
					pdf_size_cm=pdf_size_cm,
					svg_size_px=svg_size_px,
					y_label=y_label,
					x_label=x_label if x_label != None else self.default_x_label,
					title=title,
					key_position=key_position,
				)

	def get_report_dir(self):
		"""Get directory report's auxiliary files."""
		
		return self.report_dir

	def clean(self):
		"""Remove all temporary files."""

		snakemake.shell('rm -fR "{}" "{}"'.format(self.report_dir,self._html_fn))

	def get_panels(self):
		"""Get all contained panels."""
		
		return self.panels

	######################################
	######################################

	def html_fn(self):
		"""Get name of the HTML file of the report."""
		
		return self._html_fn

	######################################
	######################################

	def create_html(self):
		"""Create HTML report."""

		html_table = ""
		columns = [panel.get_html_column() for panel in self.panels]
		trs = len(columns[0])
		html_table+=os.linesep.join([
				"<tr>{}</tr>".format(
					"".join(
						[
							"<td>{}</td>".format(
								columns[col][row]
							) for col in range(len(columns))
						]
					)
				)
				for row in range(trs)
			])			

		with open(self._html_fn,"w+") as f:
			html_src="""<!DOCTYPE html>
			<html>
			<head>
				<meta charset="UTF-8" />
				<title>{name}</title>
				<style type="text/css">
					table                             {{border-collapse:collapse;}}
					td                                {{border: solid #aaaaff 1px;padding:4px;vertical-alignment:top;}}
					colgroup, thead                   {{border: solid black 2px;padding 2px;}}
					.configuration                    {{font-size:85%;}}
					.configuration, .configuration *  {{margin:0;padding:0;}}
					.formats                          {{text-align:center;margin:20px 0px;}}
					img                               {{min-width:640px}}
				</style>
			</head>
			<body>
				<h1>{name}</h1>
				<table>
				{html_table}
				</table>
			</body>
			""".format(
					html_table=html_table,
					name=self.name
				)
			f.write(html_src)

	######################################
	######################################

	@staticmethod
	def _load_x_run(x_run):
		assert len(x_run)==2
		to_return=[float(x) for x in x_run]
		assert 0< to_return[0] and to_return[0]<=1.0
		return to_return

	@staticmethod
	def _load_y_run(y_run):
		assert len(y_run)==2
		to_return=[float(x) for x in y_run]
		assert 0<=to_return[0] and to_return[0]<=100
		assert 0<=to_return[1] and to_return[1]<=100
		return to_return

	@staticmethod
	def _load_pdf_size_cm(pdf_size_cm):
		assert len(pdf_size_cm)==2
		to_return=[float(x) for x in pdf_size_cm]
		assert 0<=to_return[0]
		assert 0<=to_return[1]
		return to_return

	@staticmethod
	def _load_svg_size_px(svg_size_px):
		assert len(svg_size_px)==2
		to_return=[int(x) for x in svg_size_px]
		assert 0<=to_return[0]
		assert 0<=to_return[1]
		return to_return
