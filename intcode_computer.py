from collections import defaultdict
from enum import Enum
import json
from typing import DefaultDict, Dict, List, Tuple
from unittest.mock import ANY


class IntcodeProgramException(Exception):
    pass

class MissingInputException(Exception):
    pass

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
    def __init__(self, program: List[int], inputs: List[int]) -> None:
        self.inputs: List[int] = inputs

        self._idx: int = 0
        self._relative_base: int = 0
        self._program: DefaultDict[int, int] = defaultdict(int)
        for i, op in enumerate(program):
            self._program[i] = op

    def run(self):
        while True:
            opcode = self._program[self._idx]
            instruction = self._get_instruction(opcode)
            mode1, mode2, mode3 = self._get_modes(opcode)

            if instruction == Instruction.ADD:
                param1, param2 = self._get_params(mode1, mode2)
                result = param1 + param2
                self._set_value(mode3, 3, result)
                self._idx += 4

            elif instruction == Instruction.MULTIPLY:
                param1, param2 = self._get_params(mode1, mode2)
                result = param1 * param2
                self._set_value(mode3, 3, result)
                self._idx += 4

            elif instruction == Instruction.INPUT:
                try:
                    indata = self.inputs.pop(0)
                    self._set_value(mode1, 1, indata)
                    self._idx += 2
                except IndexError:
                    raise MissingInputException

            elif instruction == Instruction.OUTPUT:
                yield self._get_param(mode1, 1)
                self._idx += 2

            elif instruction == Instruction.JUMP_IF_TRUE:
                param1, param2 = self._get_params(mode1, mode2)
                self._idx = param2 if param1 else self._idx + 3

            elif instruction == Instruction.JUMP_IF_FALSE:
                param1, param2 = self._get_params(mode1, mode2)
                self._idx = param2 if not param1 else self._idx + 3

            elif instruction == Instruction.LESS_THAN:
                param1, param2 = self._get_params(mode1, mode2)
                result = int(param1 < param2)
                self._set_value(mode3, 3, result)
                self._idx += 4

            elif instruction == Instruction.EQUALS:
                param1, param2 = self._get_params(mode1, mode2)
                result = int(param1 == param2)
                self._set_value(mode3, 3, result)
                self._idx += 4

            elif instruction == Instruction.ADJUST_RELATIVE_BASE:
                param1 = self._get_param(mode1, 1)
                self._relative_base += param1
                self._idx += 2

            elif instruction == Instruction.ABORT:
                return

            else:
                raise IntcodeProgramException(f'Invalid instruction {instruction}.')

    def serialize_state(self) -> str:
        return json.dumps({
            'inputs': self.inputs,
            'idx': self._idx,
            'relative_base': self._relative_base,
            'program': self._program
        })

    def load_serialized_state(self, serialized_state: str) -> None:
        state: Dict[str, ANY] = json.loads(serialized_state)
        self.inputs = state['inputs']
        self._idx = state['idx']
        self._relative_base = state['relative_base']
        self._program = defaultdict(int)
        for i, op in state['program'].items():
            self._program[int(i)] = op

    def _get_modes(self, opcode: int) -> Tuple[Mode, Mode, Mode]:
        try:
            mode3, mode2, mode1 = [Mode(int(m)) for m in list(f'{opcode:05}'[:3])]
            return mode1, mode2, mode3
        except ValueError:
            raise IntcodeProgramException(f'Invalid mode.')

    def _get_instruction(self, opcode: int) -> Instruction:
        instr = str(opcode)[-2:]
        try:
            return Instruction(int(instr))
        except ValueError:
            raise IntcodeProgramException(f'Invalid instruction {instr}.')

    def _get_params(self, mode1: Mode, mode2: Mode) -> Tuple[int, int]:
        return self._get_param(mode1, 1), self._get_param(mode2, 2)

    def _get_param(self, mode: Mode, offset: int) -> int:
        if mode == Mode.POSITION:
            return self._program[self._program[self._idx + offset]]
        elif mode == Mode.IMMEDIATE:
            return self._program[self._idx + offset]
        elif mode == Mode.RELATIVE:
            return self._program[self._relative_base + self._program[self._idx + offset]]

        raise IntcodeProgramException(f'Invalid mode {mode}.')

    def _set_value(self, mode: Mode, offset: int, value: int) -> None:
        if mode == Mode.POSITION:
            self._program[self._program[self._idx + offset]] = value
        elif mode == Mode.RELATIVE:
            self._program[self._relative_base + self._program[self._idx + offset]] = value
        else:
            raise IntcodeProgramException(f'Invalid mode {mode}.')
