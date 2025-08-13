import struct
import sys
# @Author Evan Litzer           COM S 321           12/6/2024
# 
# 
# The following file disassembles a LEGV8 machine code file that is in binary format into its translated assembly code. 
# It decodes the binary into the indicated instructions of R-Type, D-Type, I-Type, CB-Type, and B-Type instructions. 
# It also handles branch labels and maintains the branch label names so that jumps to branches are correctly carried out.
#   
# It first reads the file in as input through the main function's args parameter and prints the filename at the beginning of the output.
# It then bit traverse the file and stores the instructions into instructionsList seperated by bytes. Note that this file is for big-endian format only.
# Then the list of instructions are dissassembled, first by identifying their opcode through checking it with instruction-type lists and then calling the
# corresponding decode function for that opcode. The further decode functions are responsible for identifying other patts of the instruction besides opcode
# that is tailored to the opcode/instruction-type, like Rt, Rd, etc. Once the decode functions are done, the instruction is added to a decoded-instruction list
# that represents the assembly code. Labels are also accounted for correctly through a labels list that keeps track of numbered labels as the file is decoded.
# Finally, the decoded instructions are printed in correct assembly format.


# Below are the lists of instruction names based on opcode for each instruction type. Binary byte is checked for matching these opcodes, which is then further decoded
# into other required parts of the instruction based on the opcode/instruction-type. Includes R-Type, D-Type, I-Type, CB-Type, B-Type, and B-Conditions.

R_TYPE = {0b10001011000: "ADD", 0b10001010000: "AND", 0b11001010000: "EOR", 0b11010110000: "BR", 0b11010011011: "LSL", 0b10101010000: "ORR", 0b11010011010: "LSR",
         0b11001011000: "SUB", 0b11101011000: "SUBS", 0b11111111101: "PRNT", 0b11111111100: "PRNL", 0b10011011000: "MUL", 0b11111111110: "DUMP", 0b11111111111: "HALT"}

D_TYPE = {0b11111000010: "LDUR", 0b11111000000: "STUR"}

I_TYPE = {0b1001000100: "ADDI", 0b1001001000: "ANDI", 0b1101001000: "EORI", 0b1011001000: "ORRI",
    0b1101000100: "SUBI", 0b1111000100: "SUBIS"}

CB_TYPE = {0b01010100: "B.cond", 0b10110100: "CBZ", 0b10110101: "CBNZ"}

B_TYPE = {0b000101: "B", 0b100101: "BL"}

B_CONDITIONS = {0: "EQ", 1: "NE", 2: "HS", 3: "LO", 4: "MI", 5: "PL", 6: "VS", 7: "VC",
                8: "HI", 9: "LS", 10: "GE", 11: "LT", 12: "GT", 13: "LE"}

# This is the main function responsible for calling all other functions in correct order. 
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

# The read_the_file functions is repsonsible for splitting the binary file into bytes and adding the binary byte to the instructionList. It does this in big endian format
# This sets up the instructionList to be used by other future functions, as the binary file is organized and seperated into bytes. Checks are also made if the file is empty
# or if there is an error.
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

# The disassemble function is the most crucial function of this file. It is responsible for first calling load_labels and making sure that the correct labels are loaded
# Then it calls get_opcode that gets the opcode of the instruction, before then checking if each opcode matches an opcode in the instruction type lists. 
# If the opcode does indeed match one of the opcodes in the instruction type lists, it then calls decode instruction type function for the instruction.
# If the opcode does not match one of the opcodes in the instruction type lists, then no decode is called.
# pc keeps track of the byte location in the file. Once this fucntion is complete, it returns the fully decoded instructions
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
    
    # This function is reponsible for loading the labels correctly for the instructions to then branch to at the right momemnt.
    # It checks the offset and then calculates the target address by adding the offset to the current program counter.
    # It then checks if the target address is already a label in the branch_to_labels dictionary. If it is, it adds the current label as a branch target to the label.
    # If the target address is not already a label in the branch_to_labels dictionary, it adds a new label for the target address and adds the current label as a branch target to the label.
    # This process continues until all labels are correctly loaded.
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

# get_opcode simply gets the opoce of an instruction. It checks in each instruction type list if opcodes of different lengths are in it, and if it finds that an opcode is 
# in an instruction, then it returns the corresponding opcode length that is then further used in the disassemble method. If no mathcing opcodes are found, it returns nothing.
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

# This function is responsible for decoding r-type instructions. An instruction and name are passed into the function. The binary instruction is then split according to
# the R-type format, including Rm, shat, Rn, and Rd based on what bits match each part of the instruction.
# It also checks for special cases for when output is different from other type instructions, including LSL, BR, and PRNT/PRNL/DUMP/HALT.
# The output is printed normally in its usual order if these cases are not met.
def decode_r_type(instruction, name):
    Rm = (instruction >> 16) & 0x1F  # 16-20 Bits = Rm
    shamt = (instruction >> 10) & 0x3F  # 10–15 Bits = shamt
    Rn = (instruction >> 5) & 0x1F  # 5-9 Bits = Rn
    Rd = instruction & 0x1F # 0-4 Bits = Rd

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

# This function is responsible for decoding i-type instructions. It splits the instruction into imm, Rn, and Rd based on bit order and then returns the instruction
# with correct format.
def decode_i_type(instruction, name):
    imm = (instruction >> 10) & 0xFFF  # 10-21 Bits = imm
    Rn = (instruction >> 5) & 0x1F  # 5-9 Bits = Rn
    Rd = instruction & 0x1F # 0-4 Bits = Rd    
    return f"{name} X{Rd}, X{Rn}, #{imm}"

# This function decodes the d-type instructions. It traverses the bits checking for address, Rn, and Rt before then returning it in correct format.
def decode_d_type(instruction, name):
    address = (instruction >> 12) & 0x1FF  # 10-21 Bits = address
    if address & 0x100:
        address -= 0x200
    Rn = (instruction >> 5) & 0x1F  # 5-9 Bits = Rn
    Rt = instruction & 0x1F # 0-4 Bits = Rt    
    return f"{name} X{Rt}, [X{Rn}, #{address}]"

# This function decodes the cb-type instructions. It first checks for offset and Rt by traversing the bits correctly, before then checking for a sign extension.
# Then it gets the target address using the pc and offset before using that to get the correct label. 
# It then checks if the name of the instruction is B.cond, for which it then formats it to return with the label name, or just prints the usual instruction otherwise.
def decode_cb_type(instruction, name, pc, branchLabels):
    offset = (instruction >> 5) & 0x7FFFF  # 5-23 Bits = offset
    Rt = instruction & 0x1F  # 0–4 Bits = Rt

    if offset & 0x40000:  # Check if the 19th bit (sign bit) is set
        offset -= 0x80000  # Sign extension if it is set
    
    target_address = pc + (offset << 2)  # Shift by 2
    label = branchLabels[target_address]

    if name == "B.cond":
        condition = B_CONDITIONS.get(Rt, f"unknown_cond_{Rt}")
        return f"B.{condition} {label}"
    else:    
        return f"{name} X{Rt} {label}"

# Finally, the b-type instructions are decoded here once called in disassemble. It checks for the offset and if there is a sign extension from the sign bit.
# Then it uses the pc and offset to get the correct label name in branchlabels, before returning the output in the correct format.
def decode_b_type(instruction, name, pc, branchLabels):
    offset = instruction & 0x3FFFFFF  # 0–25 = offset

    if offset & 0x2000000:  # Check if the 26th bit (sign bit) is set
        offset -= 0x4000000  # Sign extension if it is set

    target_address = pc + (offset << 2)  # Offset is in words, so shift by 2
    label = branchLabels[target_address]
    return f"{name} {label}"

# This function prints the disassembled code in accepted assembly format. 
def print_assembly(decoded_instructions):
    for pc, instruction in decoded_instructions:
        if instruction.endswith(":"):
            print(instruction)
        else:
            print(instruction)   

# This calls the main function.
if __name__=="__main__":
    main(sys.argv[1:])