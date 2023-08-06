import smbl
import snakemake
import os

import _program

DRFAST = _program.get_bin_file_path("drfast")


##########################################
##########################################


class DrFast(_program.Program):
	@classmethod
	def get_installation_files(cls):
		return [
				DRFAST,
			]

	@classmethod
	def install(cls):
		cls.git_clone("git://github.com/BilkentCompGen/drfast","")
		cls.run_make("")
		cls.install_file("drfast",DRFAST)

	@classmethod
	def supported_platforms(cls):
		return ["cygwin","linux"]
