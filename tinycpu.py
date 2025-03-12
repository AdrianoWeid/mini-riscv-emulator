ops = {"LOAD": 0x10, "ADD":0x11, "HALT":0x12, "SUB":0x13, "JUMP":0x14, "STORE":0x15, "JZ": 0x16, "CMP": 0x17}
class TinyCPU():
    def __init__(self):
        self.A = 0
        self.B = 0
        self.PC = 0
        self.memory = [0]*256

    def step(self):
        self.dump()
        op = self.memory[self.PC]

        if op == ops["LOAD"]:
            address = self.memory[self.PC+1]
            self.A = self.memory[address]
            self.PC += 2
        elif op == ops["ADD"]:
            address = self.memory[self.PC+1]
            self.A += self.memory[address]
            self.PC += 2
        elif op == ops["HALT"]:
            print("CPU stopped")
            return False
        elif op == ops["SUB"]:
            address = self.memory[self.PC+1]
            self.A -= self.memory[address]
            self.PC += 2
        elif op == ops["JUMP"]:
            address = self.memory[self.PC+1]
            self.PC = address
        elif op == ops["STORE"]:
            address = self.memory[self.PC+1]
            self.memory[address] = self.A
            self.PC += 2
        elif op == ops["JZ"]:
            address = self.memory[self.PC]
            if self.A == 0:
                self.PC = address
        elif op == ops["CMP"]:
            address = self.memory[self.PC+1]
            value = self.memory[address]

            if self.A == value:
                self.B = 0
            elif self.A > value:
                self.B = -1
            elif self.A < value:
                self.B = 1
            self.PC += 2
        else:
            print("unknown OP")
            self.PC += 1

        return True
    
    def dump(self):
        op = self.memory[self.PC]
        if op == ops["ADD"]:
            op = "ADD"
            value = self.memory[self.memory[self.PC+1]]
        elif op == ops["LOAD"]:
            op = "LOAD"
            value = self.memory[self.memory[self.PC+1]]
        elif op == ops["HALT"]:
            op = "HALT"
        elif op == ops["SUB"]:
            op = "SUB"
            value = self.memory[self.memory[self.PC+1]]
        elif op == ops["JUMP"]:
            op = "JUMP"
            value = self.memory[self.memory[self.PC+1]]
        elif op == ops["STORE"]:
            op = "STORE"
            value = self.memory[self.memory[self.PC+1]]
        elif op == ops["JZ"]:
            op = "JZ"
            value = self.memory[self.memory[self.PC+1]]
        else:
            op = f"UNKNOWN"

        instruction = op if op == "HALT" or op == "UNKNOWN"  else f"{op} {self.memory[self.PC+1]}(value: {value})"
        instruction += f": {self.memory[self.PC]}" if op == "UNKNOWN" else "" 
        print(f"\nInstruction: {instruction}\nA: {self.A}\nB: {self.B}\nPC: {self.PC}\n")


if __name__ == "__main__":
    cpu = TinyCPU()
    # Daten
    cpu.memory[34] = 5   # Startwert
    cpu.memory[35] = 3   # Additionswert
    cpu.memory[36] = 2   # Subtraktionswert
    # Programm
    cpu.memory[0] = 0x10  # LOAD 34
    cpu.memory[1] = 34
    cpu.memory[2] = 0x11  # ADD 35
    cpu.memory[3] = 35
    cpu.memory[4] = 0x13  # SUB 36
    cpu.memory[5] = 36
    cpu.memory[6] = 0x14  # JUMP 8
    cpu.memory[7] = 8
    cpu.memory[8] = 0x12  # HALT

    status = True
    while status:
        status = cpu.step()
