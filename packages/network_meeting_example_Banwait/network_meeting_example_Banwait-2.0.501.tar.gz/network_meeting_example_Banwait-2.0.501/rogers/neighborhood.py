import rogers.command_line as comline
import rogers.file_handle as filehandle


class Neighborhood():
	def __init__(self):
		pass
	
	def main(self):
		cl = comline.Command_line()
		if cl.args['h']:
			self.help()
			return
		fh = filehandle.File_handle(cl.args['i'])
		fh.parse()
		fh.export(cl.args['o'])
		return

	def help(self):
		print('\n-i\t--input\t\tNetwork file to parse.')
		print('-o\t--output')
		print('-h\t--help\n')
		return

def smain():
	stick = Neighborhood()
	stick.main()
	return
