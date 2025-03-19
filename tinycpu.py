ops = {"LOAD": 0x10, "ADD": 0x11, "HALT": 0x12, "SUB": 0x13, "JUMP": 0x14, "STORE": 0x15, "JZ": 0x16, "CMP": 0x17}

class TinyCPU():
    def __init__(self):
        self.A = 0
        self.B = 0
        self.PC = 0
        self.memory = [0] * 256

    def step(self):
        self.dump()
        op = self.memory[self.PC]
        address = self.memory[self.PC + 1]
        if op == ops["LOAD"]:
            self.A = self.memory[address] & 0xFF
            self.PC += 2
        elif op == ops["ADD"]:
            self.A = (self.A + self.memory[address]) & 0xFF
            self.PC += 2
        elif op == ops["HALT"]:
            print("CPU stopped")
            return False
        elif op == ops["SUB"]:
            self.A = (self.A - self.memory[address]) & 0xFF
            self.PC += 2
        elif op == ops["JUMP"]:
            self.PC = address
        elif op == ops["STORE"]:
            self.memory[address] = self.A & 0xFF
            self.PC += 2
        elif op == ops["JZ"]:
            if self.A == 0:
                self.PC = address
            else:
                self.PC += 2
        elif op == ops["CMP"]:
            value = self.memory[address]
            if self.A == value:
                self.B = 0
            elif self.A > value:
                self.B = 1
            else:  # self.A < value
                self.B = 2
            self.B &= 0xFF
            self.PC += 2
        else:
            print("unknown OP")
            self.PC += 1

        return True
    
    def dump(self):
        op = self.memory[self.PC]
        if op == ops["ADD"]:
            op = "ADD"
            value = self.memory[self.memory[self.PC + 1]]
        elif op == ops["LOAD"]:
            op = "LOAD"
            value = self.memory[self.memory[self.PC + 1]]
        elif op == ops["HALT"]:
            op = "HALT"
            value = None
        elif op == ops["SUB"]:
            op = "SUB"
            value = self.memory[self.memory[self.PC + 1]]
        elif op == ops["JUMP"]:
            op = "JUMP"
            value = self.memory[self.memory[self.PC + 1]]
        elif op == ops["STORE"]:
            op = "STORE"
            value = self.A  # Wert, der gespeichert wird
        elif op == ops["JZ"]:
            op = "JZ"
            value = self.memory[self.memory[self.PC + 1]]
        elif op == ops["CMP"]:
            op = "CMP"
            value = self.memory[self.memory[self.PC + 1]]
        else:
            op = "UNKNOWN"
            value = None

        instruction = op if op in ["HALT", "UNKNOWN"] else f"{op} {self.memory[self.PC + 1]}(value: {value})"
        if op == "UNKNOWN":
            instruction += f": {self.memory[self.PC]}"
        print(f"\nInstruction: {instruction}\nA: {self.A}\nB: {self.B}\nPC: {self.PC}\n")

if __name__ == "__main__":
    cpu = TinyCPU()
    # Daten
    cpu.memory[34] = 5   # Startwert
    cpu.memory[35] = 3   # Additionswert
    cpu.memory[36] = 1   # Subtraktionswert (für Schleife)
    cpu.memory[50] = 0   # Speicherplatz für STORE
    # Programm
    cpu.memory[0] = 0x10  # LOAD 34 (A = 5)
    cpu.memory[1] = 34
    cpu.memory[2] = 0x11  # ADD 35 (A = 8)
    cpu.memory[3] = 35
    cpu.memory[4] = 0x15  # STORE 50 (memory[50] = 8)
    cpu.memory[5] = 50
    cpu.memory[6] = 0x13  # SUB 36 (A -= 1)
    cpu.memory[7] = 36
    cpu.memory[8] = 0x16  # JZ 12 (springe zu HALT, wenn A = 0)
    cpu.memory[9] = 12
    cpu.memory[10] = 0x14 # JUMP 6 (zurück zu SUB)
    cpu.memory[11] = 6
    cpu.memory[12] = 0x17 # CMP 50 (vergleiche A mit 8)
    cpu.memory[13] = 50
    cpu.memory[14] = 0x12 # HALT

    status = True
    while status:
        status = cpu.step()