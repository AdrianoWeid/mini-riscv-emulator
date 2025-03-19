class RiscVCPU():
    def __init__(self):
        self.regs = [0] * 32
        self.PC = 0
        self.memory = bytearray(4096)

    def fetch(self):
        ins = int.from_bytes(self.memory[self.PC:self.PC+4], "little")
        self.PC += 4
        return ins
    
    def decode(self, ins):
        opcode = ins & 0x7F
        rd = (ins >> 7) & 0x1F
        funct3 = (ins >> 12) & 0x7
        rs1 = (ins >> 15) & 0x1F
        rs2 = (ins >> 20) & 0x1F
        imm = (ins >> 20) & 0xFFF
        if imm & 0x800:
            imm = imm - 0x1000

        return opcode, rd, funct3, rs1, rs2
    
    def step(self):
        ins = self.fetch()
        opcode, rd, funct3, rs1, rs2 = self.decode(ins)
        

cpu = RiscVCPU()
ins = 0x00500093
cpu.memory[0:4] = ins.to_bytes(4, "little")
dec = cpu.decode(ins)
for i in dec: print(hex(i))
