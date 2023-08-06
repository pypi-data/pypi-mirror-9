import smbl
import snakemake
import os

import _program

XS = _program.get_bin_file_path("XS")


##########################################
##########################################


class Xs(_program.Program):
	@classmethod
	def get_installation_files(cls):
		return [
				XS,
			]

	@classmethod
	def install(cls):
		fn=cls.download_file("http://exon.ieeta.pt/xs/xs.tar.gz","xs.tar.gz")
		dir=cls.extract_tar(fn,strip=1)
		cls.run_make(dir)
		cls.install_file("XS",XS)

	@classmethod
	def supported_platforms(cls):
		return ["cygwin","osx","linux"]
