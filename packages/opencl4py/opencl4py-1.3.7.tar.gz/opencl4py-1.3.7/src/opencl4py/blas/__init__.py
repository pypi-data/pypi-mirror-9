"""
Copyright (c) 2014, Samsung Electronics Co.,Ltd.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of Samsung Electronics Co.,Ltd..
"""

"""
opencl4py - OpenCL cffi bindings and helper classes.
URL: https://github.com/Samsung/opencl4py
Original author: Alexey Kazantsev <a.kazantsev@samsung.com>
"""

"""
Init module for BLAS cffi bindings and helper classes.
"""

from opencl4py.blas._clblas import (CLBLAS,

                                    clblasRowMajor,
                                    clblasColumnMajor,

                                    clblasNoTrans,
                                    clblasTrans,
                                    clblasConjTrans,

                                    clblasSuccess,
                                    clblasInvalidValue,
                                    clblasInvalidCommandQueue,
                                    clblasInvalidContext,
                                    clblasInvalidMemObject,
                                    clblasInvalidDevice,
                                    clblasInvalidEventWaitList,
                                    clblasOutOfResources,
                                    clblasOutOfHostMemory,
                                    clblasInvalidOperation,
                                    clblasCompilerNotAvailable,
                                    clblasBuildProgramFailure,
                                    clblasNotImplemented,
                                    clblasNotInitialized,
                                    clblasInvalidMatA,
                                    clblasInvalidMatB,
                                    clblasInvalidMatC,
                                    clblasInvalidVecX,
                                    clblasInvalidVecY,
                                    clblasInvalidDim,
                                    clblasInvalidLeadDimA,
                                    clblasInvalidLeadDimB,
                                    clblasInvalidLeadDimC,
                                    clblasInvalidIncX,
                                    clblasInvalidIncY,
                                    clblasInsufficientMemMatA,
                                    clblasInsufficientMemMatB,
                                    clblasInsufficientMemMatC,
                                    clblasInsufficientMemVecX,
                                    clblasInsufficientMemVecY)
