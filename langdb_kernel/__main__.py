from ipykernel.kernelapp import IPKernelApp
from . import LangDBKernel

IPKernelApp.launch_instance(kernel_class=LangDBKernel)