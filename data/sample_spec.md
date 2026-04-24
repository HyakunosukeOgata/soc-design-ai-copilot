# Sample SoC Module Specification

## Module: AXI4-Lite Slave Register Interface

The AXI4-Lite slave is used as a register access interface for the SoC peripherals.
It supports 32-bit address and 32-bit data width. Burst transactions are not supported.

### Clock Domain
The module operates on the system clock `aclk`. All inputs and outputs are synchronous to `aclk`.
The reset signal `aresetn` is active-low and asynchronous-assert, synchronous-deassert.

### Register Map
| Offset | Name      | Access | Description                  |
|--------|-----------|--------|------------------------------|
| 0x00   | CTRL      | RW     | Control register, bit 0 enables module |
| 0x04   | STATUS    | RO     | Status register, bit 0 = busy |
| 0x08   | DATA_IN   | RW     | Data input                   |
| 0x0C   | DATA_OUT  | RO     | Data output                  |

### Timing
The setup time for write data is 0.5 ns before the rising edge of `aclk`.
The hold time is 0.2 ns after the rising edge.
Read latency is 2 cycles.

---

## Module: SHA-256 Accelerator

The SHA-256 accelerator computes the SHA-256 hash of a streaming input.
It is compliant with FIPS 180-4. Throughput is 1 byte per clock cycle at 500 MHz.

### Power
The accelerator consumes 12 mW at 500 MHz, 0.9 V.
Clock gating is applied when no input is valid for more than 4 cycles.

### Interface
The accelerator has a streaming AXI4-Stream input and a 256-bit output port.
The output `hash_valid` signal is asserted when the hash computation is complete.
Computation takes 64 + N cycles where N is the input length in bytes.

---

## Module: Clock Domain Crossing FIFO

A dual-clock asynchronous FIFO is used to safely transfer data between two clock domains.
Depth is configurable (default 16 entries). Each entry is 32 bits.

### Metastability Handling
A 2-stage synchronizer is used on the read and write pointers.
Gray-code encoding prevents multi-bit transitions from causing incorrect synchronization.

### Empty / Full Detection
The empty flag is generated in the read clock domain.
The full flag is generated in the write clock domain.
Pessimistic detection is used: the FIFO may report full when there is one free entry,
but it will never report not-full when it is actually full.

---

## Module: SystemVerilog Coding Style Notes

Always use `always_ff` for sequential logic and `always_comb` for combinational logic.
Do NOT use `always @*` in modern designs because it cannot be statically checked by tools.

The keyword `priority` and `unique` should be added to case statements to enable lint checking.
Avoid `tristate` outputs inside the chip — only use them at top-level pads.

Use non-blocking assignment `<=` inside `always_ff`. Use blocking assignment `=` inside `always_comb`.
Mixing them causes simulation-synthesis mismatch.

### Reset Strategy
The synchronizer for asynchronous reset uses two flip-flops on the reset deassertion path.
This is sometimes called a `reset synchronizer` or `arstn synchronizer` in textbooks.
