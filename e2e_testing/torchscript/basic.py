# Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
# Also available under a BSD-style license. See LICENSE.

import torch

from torch_mlir_e2e_test.torchscript.framework import TestUtils
from torch_mlir_e2e_test.torchscript.registry import register_test_case
from torch_mlir_e2e_test.torchscript.annotations import annotate_args, export

# ==============================================================================


class MmModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1], torch.float32, True),
        ([-1, -1], torch.float32, True),
    ])
    def forward(self, lhs, rhs):
        return torch.mm(lhs, rhs)


@register_test_case(module_factory=lambda: MmModule())
def MmModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(4, 4), tu.rand(4, 4))


@register_test_case(module_factory=lambda: MmModule())
def MmModule_chained(module, tu: TestUtils):
    res = module.forward(tu.rand(4, 4), tu.rand(4, 4))
    module.forward(res, res)

# ==============================================================================


class BmmModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1, -1], torch.float32, True),
        ([-1, -1, -1], torch.float32, True),
    ])
    def forward(self, lhs, rhs):
        return torch.bmm(lhs, rhs)


@register_test_case(module_factory=lambda: BmmModule())
def BmmModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(3, 4, 5), tu.rand(3, 5, 4))


# ==============================================================================


# A subgraph with multiple mm ops.
class MmDagModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([4, 4], torch.float32, True),
        ([4, 4], torch.float32, True),
    ])
    def forward(self, lhs, rhs):
        return torch.mm(lhs, torch.mm(lhs, rhs))


@register_test_case(module_factory=lambda: MmDagModule())
def MmDagModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(4, 4), tu.rand(4, 4))


# ==============================================================================


class MmTanhModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1], torch.float32, True),
        ([-1, -1], torch.float32, True),
    ])
    def forward(self, lhs, rhs):
        return torch.tanh(self.matmul(lhs, rhs))

    def matmul(self, lhs, rhs):
        return torch.mm(lhs, rhs)

# ==============================================================================


@register_test_case(module_factory=lambda: MmTanhModule())
def MmTanhModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(4, 2), tu.rand(2, 4))

# ==============================================================================


class AddmmModuleFloat(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1], torch.float32, True),
        ([-1, -1], torch.float32, True),
        ([-1, -1], torch.float32, True),
    ])
    def forward(self, M, mat1, mat2):
        return torch.addmm(M, mat1, mat2, beta=3.0, alpha=7.0)


@register_test_case(module_factory=lambda: AddmmModuleFloat())
def AddmmModuleFloat_basic(module, tu: TestUtils):
    module.forward(tu.rand(4, 4), tu.rand(4, 2), tu.rand(2, 4))

#  ==============================================================================


class AddmmModuleBroadcastable(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([1, -1], torch.float32, True),
        ([-1, -1], torch.float32, True),
        ([-1, -1], torch.float32, True),
    ])
    def forward(self, M, mat1, mat2):
        return torch.addmm(M, mat1, mat2, beta=2.0, alpha=7.0)


@register_test_case(module_factory=lambda: AddmmModuleBroadcastable())
def AddmmModule_broadcastable(module, tu: TestUtils):
    module.forward(tu.rand(1, 2), tu.rand(3, 2), tu.rand(2, 2))

#  ==============================================================================


class AddmmModuleDifferentRankBroadcastable(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1], torch.float32, True),
        ([-1, -1], torch.float32, True),
        ([-1, -1], torch.float32, True),
    ])
    def forward(self, M, mat1, mat2):
        return torch.addmm(M, mat1, mat2, beta=11.0, alpha=7.0)


@register_test_case(module_factory=lambda: AddmmModuleDifferentRankBroadcastable())
def AddmmModule_differentRankBroadcastable(module, tu: TestUtils):
    module.forward(tu.rand(3), tu.rand(3, 2), tu.rand(2, 3))

#  ==============================================================================


class AdaptiveAvgPool2dModule(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.aap2d = torch.nn.AdaptiveAvgPool2d((1, 1))

    @export
    @annotate_args([
        None,
        ([-1, -1, -1, -1], torch.float32, True),
    ])
    def forward(self, x):
        return self.aap2d(x)


@register_test_case(module_factory=lambda: AdaptiveAvgPool2dModule())
def AdaptiveAvgPool2dModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(10, 3, 8, 9))

# ==============================================================================


class FlattenStaticModule(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.flat = torch.nn.Flatten(2, 4)

    @export
    @annotate_args([
        None,
        ([10, 3, 8, 9, 3, 4], torch.float32, True),
    ])
    def forward(self, x):
        return self.flat(x)


@register_test_case(module_factory=lambda: FlattenStaticModule())
def FlattenStaticModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(10, 3, 8, 9, 3, 4))

# ==============================================================================


class FlattenRank0Module(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.flat = torch.nn.Flatten(-1, -1)

    @export
    @annotate_args([
        None,
        ([], torch.float32, True),
    ])
    def forward(self, x):
        return self.flat(x)


@register_test_case(module_factory=lambda: FlattenRank0Module())
def FlattenRank0Module_basic(module, tu: TestUtils):
    module.forward(torch.tensor(4.0))

# ==============================================================================


class FlattenDynamicModule(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.flat = torch.nn.Flatten(2, 4)

    @export
    @annotate_args([
        None,
        ([-1, -1, -1, 9, 3, -1], torch.float32, True),
    ])
    def forward(self, x):
        return self.flat(x)


@register_test_case(module_factory=lambda: FlattenDynamicModule())
def FlattenDynamicModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(10, 3, 8, 9, 3, 4))

# ==============================================================================


class MaxPool2dModule(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.mp2d = torch.nn.MaxPool2d(kernel_size=[6, 8],
                                       stride=[2, 2],
                                       padding=[3, 4],
                                       dilation=2)

    @export
    @annotate_args([
        None,
        ([-1, -1, -1, -1], torch.float32, True),
    ])
    def forward(self, x):
        return self.mp2d(x)

# ==============================================================================


@register_test_case(module_factory=lambda: MaxPool2dModule())
def MaxPool2dModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(1, 1, 20, 20) - 0.5)


class TransposeIntModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([3, 4, 2], torch.float32, True),
    ])
    def forward(self, x):
        return torch.transpose(x, 0, 1)

# ==============================================================================


@register_test_case(module_factory=lambda: TransposeIntModule())
def TransposeIntModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(3, 4, 2))

class PermuteModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([3, 4, 2], torch.float32, True)
    ])
    def forward(self, x):
        return x.permute(0, 2, 1)

@register_test_case(module_factory=lambda: PermuteModule())
def PermuteModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(3, 4, 2))

# ==============================================================================

class TransposeIntNegDimsModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([3, 4, 2], torch.float32, True),
    ])
    def forward(self, x):
        return torch.transpose(x, -1, -2)

# ==============================================================================


@register_test_case(module_factory=lambda: TransposeIntNegDimsModule())
def TransposeIntNegDimsModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(3, 4, 2))


class PermuteNegativeIndexModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([3, 4, 2], torch.float32, True)
    ])
    def forward(self, x):
        return x.permute(0, -1, 1)

# ==============================================================================

@register_test_case(module_factory=lambda: PermuteNegativeIndexModule())
def PermuteNegativeIndexModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(3, 4, 2))
class TensorsConcatModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1, -1], torch.float32, True),
        ([-1, -1, -1], torch.float32, True),
        ([-1, -1, -1], torch.float32, True),
    ])
    def forward(self, x, y, z):
        return torch.cat([x, y, z], 1)


@register_test_case(module_factory=lambda: TensorsConcatModule())
def TensorsConcatModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(2, 2, 4), tu.rand(2, 1, 4), tu.rand(2, 3, 4))

# ==============================================================================


class GatherModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1, -1], torch.float32, True),
        ([-1, -1, -1], torch.int64, True),
    ])
    def forward(self, tensor, indices):
        return torch.gather(tensor, 2, indices)


@register_test_case(module_factory=lambda: GatherModule())
def GatherModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(2, 3, 4), torch.tensor([[[1, 2, 3], [1, 2, 3]]]))

# ==============================================================================

class AddSizeIntModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1], torch.float32, True),
    ])
    def forward(self, tensor):
        # This is a workaround for not supporting scalar arguments.
        # TODO: pass in dim as an argument to the forward method when scalar
        # arguments are supported.
        return tensor.add(tensor, alpha=tensor.size(1))


@register_test_case(module_factory=lambda: AddSizeIntModule())
def AddSizeIntModule_basic(module, tu: TestUtils):
    module.forward(torch.randn(3, 3))

# ==============================================================================


class AddSizeIntNegDimModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1], torch.float32, True),
    ])
    def forward(self, tensor):
        # This is a workaround for not supporting scalar arguments.
        # TODO: pass in dim as an argument to the forward method when scalar
        # arguments are supported.
        return tensor.add(tensor, alpha=tensor.size(-2))


@register_test_case(module_factory=lambda: AddSizeIntNegDimModule())
def AddSizeIntNegDimModule_basic(module, tu: TestUtils):
    module.forward(torch.randn(3, 3))

# ==============================================================================

class EmbeddingModule(torch.nn.Module):
    def __init__(self):
        super().__init__()
        torch.manual_seed(0)
        self.embed = torch.nn.Embedding(num_embeddings=100,
                                        embedding_dim=50,
                                        padding_idx=4)

    @export
    @annotate_args([
        None,
        ([-1, -1], torch.int64, True),
    ])
    def forward(self, indices):
        return self.embed.forward(indices)


@register_test_case(module_factory=lambda: EmbeddingModule())
def EmbeddingModule_basic(module, tu: TestUtils):
    module.forward(torch.randint(100, (3, 3)))

# ==============================================================================

class SoftmaxIntModule(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.softmax = torch.nn.Softmax(2)

    @export
    @annotate_args([
        None,
        ([-1, -1, -1], torch.float32, True),
    ])
    def forward(self, tensor):
        return self.softmax.forward(tensor)


@register_test_case(module_factory=lambda: SoftmaxIntModule())
def SoftmaxIntModule_basic(module, tu: TestUtils):
    module.forward(torch.randn(3, 2, 4))

class _SoftmaxModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1, -1], torch.float32, True),
    ])
    def forward(self, tensor):
        return torch.ops.aten._softmax(tensor, 0, False)


@register_test_case(module_factory=lambda: _SoftmaxModule())
def _SoftmaxModule_basic(module, tu: TestUtils):
    module.forward(torch.randn(3, 2, 4))

# ==============================================================================


class SoftmaxIntNegDimModule(torch.nn.Module):
    def __init__(self):
        super().__init__()
        torch.manual_seed(0)
        self.softmax = torch.nn.Softmax(-2)

    @export
    @annotate_args([
        None,
        ([-1, -1, -1], torch.float32, True),
    ])
    def forward(self, tensor):
        return self.softmax.forward(tensor)


@register_test_case(module_factory=lambda: SoftmaxIntNegDimModule())
def SoftmaxIntNegDimModule_basic(module, tu: TestUtils):
    module.forward(torch.randn(3, 2, 4))

# ==============================================================================


class SoftmaxIntArgTypeF64Module(torch.nn.Module):
    def __init__(self):
        super().__init__()
        torch.manual_seed(0)
        self.softmax = torch.nn.Softmax(2)

    @export
    @annotate_args([
        None,
        ([-1, -1, -1], torch.float64, True),
    ])
    def forward(self, tensor):
        return self.softmax.forward(tensor)

@register_test_case(module_factory=lambda: SoftmaxIntArgTypeF64Module())
def SoftmaxIntArgTypeF64Module_basic(module, tu: TestUtils):
    module.forward(torch.randn(3, 2, 4).double())

# ==============================================================================

class BroadcastToModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1, 1], torch.float32, True),
    ])
    def forward(self, x):
        return torch.broadcast_to(x, [1, -1, -1, 4])


@register_test_case(module_factory=lambda: BroadcastToModule())
def BroadcastToModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(3, 1, 1))

# ==============================================================================

class ExpandModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1, 1], torch.float32, True),
    ])
    def forward(self, x):
        return x.expand([1, -1, -1, 4])


@register_test_case(module_factory=lambda: ExpandModule())
def ExpandModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(3, 1, 1))

# ==============================================================================


class OnesModuleInt(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
    ])
    def forward(self):
        return torch.ones(3, 4, dtype=torch.int64)

@register_test_case(module_factory=lambda: OnesModuleInt())
def OnesModuleInt_basic(module, tu: TestUtils):
    module.forward()

# ==============================================================================

class OnesModuleFloat(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
    ])
    def forward(self):
        return torch.ones(3, 4, dtype=torch.float32)

@register_test_case(module_factory=lambda: OnesModuleFloat())
def OnesModuleFloat_basic(module, tu: TestUtils):
    module.forward()


class OnesModuleFalsePinMemory(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
    ])
    def forward(self):
        return torch.ones(3, 4, dtype=torch.float32, pin_memory=False)

@register_test_case(module_factory=lambda: OnesModuleFalsePinMemory())
def OnesModuleFalsePinMemory_basic(module, tu: TestUtils):
    module.forward()

# ==============================================================================

class ContiguousModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1], torch.float32, True),
    ])
    def forward(self, x):
        return x.contiguous()


@register_test_case(module_factory=lambda: ContiguousModule())
def ContiguousModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(3, 1))
    
class TensorToInt(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([], torch.int64, True),
    ])
    def forward(self, x):
        return int(x)


@register_test_case(module_factory=lambda: TensorToInt())
def TensorToInt_basic(module, tu: TestUtils):
    module.forward(torch.randint(10,[]))

class LogSoftmaxIntModule(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.log_softmax = torch.nn.LogSoftmax(2)

    @export
    @annotate_args([
        None,
        ([-1, -1, -1], torch.float64, True),
    ])
    def forward(self, tensor):
        return self.log_softmax.forward(tensor)

@register_test_case(module_factory=lambda: LogSoftmaxIntModule())
def LogSoftmaxIntModule_basic(module, tu: TestUtils):
    module.forward(torch.randn(3, 2, 4).double())


class NumToTensorIntModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
    ])

    def forward(self):
        return torch.ops.prim.NumToTensor(1)

@register_test_case(module_factory=lambda: NumToTensorIntModule())
def NumToTensorIntModule_basic(module, tu: TestUtils):
    module.forward()


class NumToTensorFloatModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
    ])

    def forward(self):
        return torch.ops.prim.NumToTensor(1.0)


@register_test_case(module_factory=lambda: NumToTensorFloatModule())
def NumToTensorFloatModule_basic(module, tu: TestUtils):
    module.forward()

# ==============================================================================

# This test can be removed once we have one real op returning 3 float32 tensors
class ReturnThreeTensorFloat32(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1], torch.float32, True),
        ([-1, -1], torch.float32, True),
        ([-1, -1], torch.float32, True),
    ])
    def forward(self, a, b, c):
        return a, b, c

@register_test_case(module_factory=lambda: ReturnThreeTensorFloat32())
def ReturnThreeTensorFloat32_basic(module, tu: TestUtils):
    module.forward(tu.rand(2, 3), tu.rand(2, 3), tu.rand(2, 3))

class AddCMulModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,   
        ([-1, -1], torch.float32, True),
        ([-1, -1], torch.float32, True),
        ([-1, -1], torch.float32, True),
    ])

    def forward(self, input, tensor1, tensor2):
        return torch.addcmul(input, tensor1, tensor2, value=1.0)

@register_test_case(module_factory=lambda: AddCMulModule())
def AddCMulModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(1,3), tu.rand(1,3), tu.rand(1,3))

class AddCDivModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,   
        ([-1, -1], torch.float32, True),
        ([-1, -1], torch.float32, True),
        ([-1, -1], torch.float32, True),
    ])

    def forward(self, input, tensor1, tensor2):
        return torch.addcdiv(input, tensor1, tensor2, value=1.0)

@register_test_case(module_factory=lambda: AddCDivModule())
def AddCDivModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(1,3), tu.rand(1,3), tu.rand(1,3))

# ==============================================================================


class DropoutModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1], torch.float32, True),
    ])

    def forward(self, x):
        return torch.dropout(x, 0.0, False)


@register_test_case(module_factory=lambda: DropoutModule())
def DropoutModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(3, 4))


class Fill_TensorFloat64WithFloat32(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1, -1], torch.float32, True),
    ])
    def forward(self, tensor):
        return torch.ops.aten.fill_(tensor, 3.0)

@register_test_case(module_factory=lambda: Fill_TensorFloat64WithFloat32())
def Fill_TensorFloat64WithFloat32_basic(module, tu: TestUtils):
    module.forward(torch.randn(3, 2, 4))


class Fill_TensorFloat64WithFloat64(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1, -1], torch.float64, True),
    ])
    def forward(self, tensor):
        return torch.ops.aten.fill_(tensor, 3.0)

@register_test_case(module_factory=lambda: Fill_TensorFloat64WithFloat64())
def Fill_TensorFloat64WithFloat64_basic(module, tu: TestUtils):
    module.forward(torch.randn(3, 2, 4).to(torch.float64))


class Fill_TensorFloat64WithInt64(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1, -1], torch.float64, True),
    ])
    def forward(self, tensor):
        return torch.ops.aten.fill_(tensor, 3)

@register_test_case(module_factory=lambda: Fill_TensorFloat64WithInt64())
def Fill_TensorFloat64WithInt64_basic(module, tu: TestUtils):
    module.forward(torch.randn(3, 2, 4).to(torch.float64))


class MeanModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([3, 4], torch.float32, True),
    ])
    def forward(self, x):
        return torch.mean(x)


@register_test_case(module_factory=lambda: MeanModule())
def MeanModule_basic(module, tu: TestUtils):
    module.forward(torch.randn(3, 4))


class MeanDynamicSizesModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1], torch.float32, True),
    ])
    def forward(self, x):
        return torch.mean(x)


@register_test_case(module_factory=lambda: MeanDynamicSizesModule())
def MeanDynamicSizesModule_basic(module, tu: TestUtils):
    module.forward(torch.randn(3, 4))


class NumelModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1, -1], torch.float32, True),
    ])
    def forward(self, input):
        return torch.numel(input)

@register_test_case(module_factory=lambda: NumelModule())
def NumelModule_basic(module, tu: TestUtils):
    module.forward(tu.rand(4, 3, 5))


class NumelZeroRankModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([], torch.int64, True),
    ])
    def forward(self, input):
        return torch.numel(input)

@register_test_case(module_factory=lambda: NumelZeroRankModule())
def NumelZeroRankModule_basic(module, tu: TestUtils):
    module.forward(torch.randint(10,[]))


class ZerosModuleInt2D(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
    ])
    def forward(self):
        return torch.zeros(3, 4, dtype=torch.int64)

@register_test_case(module_factory=lambda: ZerosModuleInt2D())
def ZerosModuleInt2D_basic(module, tu: TestUtils):
    module.forward()


class ZerosModuleInt3D(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
    ])
    def forward(self):
        return torch.zeros(3, 4, 5, dtype=torch.int64)

@register_test_case(module_factory=lambda: ZerosModuleInt3D())
def ZerosModuleInt3D_basic(module, tu: TestUtils):
    module.forward()


class ZerosModuleFloat2D(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
    ])
    def forward(self):
        return torch.zeros(3, 4, dtype=torch.float32)

@register_test_case(module_factory=lambda: ZerosModuleFloat2D())
def ZerosModuleFloat2D_basic(module, tu: TestUtils):
    module.forward()


class ZerosModuleFloat3D(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
    ])
    def forward(self):
        return torch.zeros(3, 4, 5, dtype=torch.float32)

@register_test_case(module_factory=lambda: ZerosModuleFloat3D())
def ZerosModuleFloat3D_basic(module, tu: TestUtils):
    module.forward()


class ZerosModuleFalsePinMemory(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
    ])
    def forward(self):
        return torch.zeros(3, 4, dtype=torch.float32, pin_memory=False)

@register_test_case(module_factory=lambda: ZerosModuleFalsePinMemory())
def ZerosModuleFalsePinMemory_basic(module, tu: TestUtils):
    module.forward()


class BoolTensorReturnFalseModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1], torch.bool, True),
    ])
    def forward(self, a):
        return a


@register_test_case(module_factory=lambda: BoolTensorReturnFalseModule())
def BoolTensorReturnFalseModule_basic(module, tu: TestUtils):
    module.forward(torch.tensor([0, 0], dtype=torch.bool))


class BoolTensorReturnTrueModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1], torch.bool, True),
    ])
    def forward(self, a):
        return a


@register_test_case(module_factory=lambda: BoolTensorReturnTrueModule())
def BoolTensorReturnTrueModule_basic(module, tu: TestUtils):
    module.forward(torch.tensor([1, 1, 1, 1, 1], dtype=torch.bool))


class BoolTensorReturnMixedModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @export
    @annotate_args([
        None,
        ([-1, -1], torch.bool, True),
    ])
    def forward(self, a):
        return a


@register_test_case(module_factory=lambda: BoolTensorReturnMixedModule())
def BoolTensorReturnMixedModule_basic(module, tu: TestUtils):
    module.forward(torch.tensor([[1, 0], [0,1]], dtype=torch.bool))