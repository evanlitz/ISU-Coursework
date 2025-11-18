import struct
import sys

R_TYPE = {0b10001011000: "ADD", 0b10001010000: "AND", 0b11001010000: "EOR", 0b11010110000: "BR", 0b11010011011: "LSL", 0b10101010000: "ORR", 0b11010011010: "LSR",
         0b11001011000: "SUB", 0b11101011000: "SUBS", 0b11111111101: "PRNT", 0b11111111100: "PRNL", 0b10011011000: "MUL", 0b11111111110: "DUMP", 0b11111111111: "HALT"}

D_TYPE = {0b11111000010: "LDUR", 0b11111000000: "STUR"}

I_TYPE = {0b1001000100: "ADDI", 0b1001001000: "ANDI", 0b1101001000: "EORI", 0b1011001000: "ORRI",
    0b1101000100: "SUBI", 0b1111000100: "SUBIS"}

CB_TYPE = {0b01010100: "B.cond", 0b10110100: "CBZ", 0b10110101: "CBNZ"}

B_TYPE = {0b000101: "B", 0b100101: "BL"}

B_CONDITIONS = {0: "EQ", 1: "NE", 2: "HS", 3: "LO", 4: "MI", 5: "PL", 6: "VS", 7: "VC",
                8: "HI", 9: "LS", 10: "GE", 11: "LT", 12: "GT", 13: "LE"}

def main(args):
    print("Starting main function...")

    if len(args) < 1:
        print("Error: Invalid input file.")
        sys.exit(1)

    filename = args[0]
    print(f"Input file: {filename}")

    instructions = read_the_file(filename)
    print(f"Read {len(instructions)} instructions.")

    decoded_instructions = disassemble(instructions)
    print("Disassembled instructions:")

    print_assembly(decoded_instructions)

def read_the_file(filename):
    instructionList = []

    try:
        with open(filename, 'rb') as file:
            while (byte := file.read(4)):
                instruction = int.from_bytes(byte, byteorder='big')
                instructionList.append(instruction)

    except FileNotFoundError:
        print(f"Error: File not found: {filename}")
        sys.exit(1)

    except Exception as e:
        print(f"Error: File not found: {e}")
        sys.exit(1)

    if not instructionList:
        print(f"Error: The file '{filename}' is empty")
        sys.exit(1)

    return instructionList

def disassemble(instructions):
    branchLabels = load_labels(instructions)
    pc = 0
    decoded_instructions = []

    for instruction in instructions:
        if pc in branchLabels:
            decoded_instructions.append((pc, f"{branchLabels[pc]}:"))

        opcode = get_opcode(instruction)
        decoded_instruction = None

        if opcode in R_TYPE:
            name = R_TYPE[opcode]
            decoded_instruction = decode_r_type(instruction, name)
        elif opcode in D_TYPE:
            name = D_TYPE[opcode]
            decoded_instruction = decode_d_type(instruction, name)
        elif opcode in I_TYPE:
            name = I_TYPE[opcode]
            decoded_instruction = decode_i_type(instruction, name)
        elif opcode in CB_TYPE:
            name = CB_TYPE[opcode]
            decoded_instruction = decode_cb_type(instruction, name, pc, branchLabels)
        elif opcode in B_TYPE:
            name = B_TYPE[opcode]
            decoded_instruction = decode_b_type(instruction, name, pc, branchLabels)           
        else:
            decoded_instruction = f".word 0x{instruction:08X}"

        decoded_instructions.append((pc, decoded_instruction))

        pc += 4

    return decoded_instructions

def load_labels(instructions):
    branch_to_labels = {}
    countLabels = 0
    pc = 0

    for instruction in instructions:
        opcode = get_opcode(instruction)

        if opcode in CB_TYPE or opcode in B_TYPE:
            if opcode in CB_TYPE:
                offset = (instruction >> 5) & 0x7FFFF
                if offset & 0x40000:
                    offset -= 0x80000
            elif opcode in B_TYPE:
                offset = instruction & 0x3FFFFFF
                if offset & 0x2000000:
                    offset -= 0x4000000

            target_address = pc + (offset << 2)

            if target_address not in branch_to_labels:
                branch_to_labels[target_address] = f"label{countLabels}"
                countLabels += 1

        pc += 4

    return branch_to_labels

def get_opcode(instruction):
    opcode_11 = (instruction >> 21) & 0x7FF
    opcode_10 = (instruction >> 22) & 0x3FF
    opcode_8 = (instruction >> 24) & 0xFF
    opcode_6 = (instruction >> 26) & 0x3F

    if opcode_11 in R_TYPE:
        return opcode_11

    elif opcode_11 in D_TYPE:
        return opcode_11

    elif opcode_10 in I_TYPE:
        return opcode_10

    elif opcode_8 in CB_TYPE:
        return opcode_8

    elif opcode_6 in B_TYPE:
        return opcode_6

    return None


def decode_r_type(instruction, name):
    Rm = (instruction >> 16) & 0x1F
    shamt = (instruction >> 10) & 0x3F
    Rn = (instruction >> 5) & 0x1F
    Rd = instruction & 0x1F

    if name == "LSL" or name == "LSR":
        return f"{name} X{Rd}, X{Rn}, #{shamt}"
    elif name == "BR":
        return f"{name} X{Rn}"
    elif name in ["PRNT", "PRNL", "DUMP", "HALT"]:
        if name == "PRNT":
            return f"{name} X{Rd}"
        return name
    else:
        return f"{name} X{Rd}, X{Rn}, X{Rm}"

def decode_i_type(instruction, name):
    imm = (instruction >> 10) & 0xFFF
    Rn = (instruction >> 5) & 0x1F
    Rd = instruction & 0x1F
    return f"{name} X{Rd}, X{Rn}, #{imm}"

def decode_d_type(instruction, name):
    address = (instruction >> 12) & 0x1FF
    if address & 0x100:
        address -= 0x200
    Rn = (instruction >> 5) & 0x1F
    Rt = instruction & 0x1F
    return f"{name} X{Rt}, [X{Rn}, #{address}]"


def decode_cb_type(instruction, name, pc, branchLabels):
    offset = (instruction >> 5) & 0x7FFFF
    Rt = instruction & 0x1F

    if offset & 0x40000:
        offset -= 0x80000

    target_address = pc + (offset << 2)
    label = branchLabels[target_address]

    if name == "B.cond":
        condition = B_CONDITIONS.get(Rt, f"unknown_cond_{Rt}")
        return f"B.{condition} {label}"
    else:
        return f"{name} X{Rt} {label}"

def decode_b_type(instruction, name, pc, branchLabels):
    offset = instruction & 0x3FFFFFF

    if offset & 0x2000000:
        offset -= 0x4000000

    target_address = pc + (offset << 2)
    label = branchLabels[target_address]
    return f"{name} {label}"

def print_assembly(decoded_instructions):
    for pc, instruction in decoded_instructions:
        if instruction.endswith(":"):
            print(instruction)
        else:
            print(instruction)

if __name__=="__main__":
    main(sys.argv[1:])
