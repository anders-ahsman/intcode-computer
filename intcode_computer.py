from collections import defaultdict
from enum import Enum
from typing import DefaultDict, List, Tuple


class Mode(Enum):
    POSITION = 0
    IMMEDIATE = 1
    RELATIVE = 2

class Instruction(Enum):
    ADD = 1
    MULTIPLY = 2
    INPUT = 3
    OUTPUT = 4
    JUMP_IF_TRUE = 5
    JUMP_IF_FALSE = 6
    LESS_THAN = 7
    EQUALS = 8
    ADJUST_RELATIVE_BASE = 9
    ABORT = 99

class IntcodeComputer:
    def __init__(self, program: List[int]):
        self.idx: int = 0
        self.relative_base: int = 0
        self.inputs: List[int] = []
        self.program: DefaultDict[int, int] = defaultdict(int)
        for i, op in enumerate(program):
            self.program[i] = op

    def run(self):
        while True:
            opcode = self.program[self.idx]
            instruction = self.get_instruction(opcode)
            mode1, mode2, mode3 = self.get_modes(opcode)

            if instruction == Instruction.ADD:
                param1, param2 = self.get_params(mode1, mode2)
                result = param1 + param2
                self.set_value(mode3, 3, result)
                self.idx += 4

            elif instruction == Instruction.MULTIPLY:
                param1, param2 = self.get_params(mode1, mode2)
                result = param1 * param2
                self.set_value(mode3, 3, result)
                self.idx += 4

            elif instruction == Instruction.INPUT:
                indata = self.inputs.pop(0)
                self.set_value(mode1, 1, indata)
                self.idx += 2

            elif instruction == Instruction.OUTPUT:
                yield self.get_param(mode1, 1)
                self.idx += 2

            elif instruction == Instruction.JUMP_IF_TRUE:
                param1, param2 = self.get_params(mode1, mode2)
                self.idx = param2 if param1 else self.idx + 3

            elif instruction == Instruction.JUMP_IF_FALSE:
                param1, param2 = self.get_params(mode1, mode2)
                self.idx = param2 if not param1 else self.idx + 3

            elif instruction == Instruction.LESS_THAN:
                param1, param2 = self.get_params(mode1, mode2)
                result = int(param1 < param2)
                self.set_value(mode3, 3, result)
                self.idx += 4

            elif instruction == Instruction.EQUALS:
                param1, param2 = self.get_params(mode1, mode2)
                result = int(param1 == param2)
                self.set_value(mode3, 3, result)
                self.idx += 4

            elif instruction == Instruction.ADJUST_RELATIVE_BASE:
                param1 = self.get_param(mode1, 1)
                self.relative_base += param1
                self.idx += 2

            elif instruction == Instruction.ABORT:
                return

            else:
                raise Exception(f'Unknown instruction {instruction}')

    def get_modes(self, opcode: int) -> Tuple[Mode, Mode, Mode]:
        mode3, mode2, mode1 = [Mode(int(m)) for m in list(f'{opcode:05}'[:3])]
        return mode1, mode2, mode3

    def get_instruction(self, opcode: int) -> Instruction:
        return Instruction(int(str(opcode)[-2:]))

    def get_params(self, mode1: Mode, mode2: Mode) -> Tuple[int, int]:
        return self.get_param(mode1, 1), self.get_param(mode2, 2)

    def get_param(self, mode: Mode, offset: int) -> int:
        if mode == Mode.POSITION:
            return self.program[self.program[self.idx + offset]]
        elif mode == Mode.IMMEDIATE:
            return self.program[self.idx + offset]
        elif mode == Mode.RELATIVE:
            return self.program[self.relative_base + self.program[self.idx + offset]]

        raise Exception(f'Unknown mode {mode}')

    def set_value(self, mode: Mode, offset: int, value: int) -> None:
        if mode == Mode.POSITION:
            self.program[self.program[self.idx + offset]] = value
        elif mode == Mode.RELATIVE:
            self.program[self.relative_base + self.program[self.idx + offset]] = value
        else:
            raise Exception(f'Unknown mode {mode}')
