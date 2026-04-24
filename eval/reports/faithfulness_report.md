# Faithfulness Eval Report

- Faithfulness: **13/15 = 86.67%**
- Refusal Accuracy: **1/1 = 100.00%**

## Per-Question Detail

| ID | Type | Result | Question | Answer (truncated) | Judge |
|----|------|--------|----------|--------------------|-------|
| q01 | faithful | FAIL (refused) | What is the power consumption of the SHA-256 accelerator? | I don't know based on the provided documents. | - |
| q02 | faithful | PASS | How does the FIFO handle metastability? | The FIFO handles metastability by using a 2-stage synchronizer on the read and write pointers. Additionally, Gray-code e | The answer accurately reflects the information provided in the context regarding |
| q03 | faithful | PASS | What is the read latency of the AXI4-Lite slave? | The read latency of the AXI4-Lite slave is 2 cycles. | The answer directly states the read latency as mentioned in the context. |
| q04 | faithful | PASS | What is the setup time for write data on AXI4-Lite? | The setup time for write data on AXI4-Lite is 0.5 ns before the rising edge of `aclk`. | The answer is directly supported by the context provided. |
| q05 | faithful | PASS | What is the address width of the AXI4-Lite slave? | The address width of the AXI4-Lite slave is 32 bits. | The context explicitly states that the AXI4-Lite slave supports a 32-bit address |
| q06 | faithful | PASS | Which standard does the SHA-256 accelerator comply with? | The SHA-256 accelerator is compliant with FIPS 180-4. | The context explicitly states that the SHA-256 accelerator is compliant with FIP |
| q07 | faithful | PASS | When is clock gating applied in the SHA-256 accelerator? | Clock gating is applied when no input is valid for more than 4 cycles. | The answer directly reflects the information provided in the context regarding c |
| q08 | faithful | PASS | What is the default depth of the CDC FIFO? | The default depth of the CDC FIFO is 16 entries. | The answer is directly supported by the context stating that the default depth o |
| q09 | faithful | PASS | Why use Gray-code in the CDC FIFO? | Gray-code encoding is used in the CDC FIFO to prevent multi-bit transitions from causing incorrect synchronization. | The answer accurately reflects the information provided in the context about Gra |
| q10 | faithful | PASS | Which keyword should be used for sequential logic in modern SystemVerilog? | The keyword that should be used for sequential logic in modern SystemVerilog is `always_ff`. | The answer correctly states that `always_ff` should be used for sequential logic |
| q11 | faithful | PASS | Why should always @* be avoided? | Always @* should be avoided in modern designs because it cannot be statically checked by tools. | The answer accurately reflects the context regarding the avoidance of 'always @* |
| q12 | faithful | PASS | What assignment operator should be used inside always_ff? | Use non-blocking assignment `<=` inside `always_ff`. | The answer directly reflects the information provided in the context regarding t |
| q13 | faithful | PASS | What is a reset synchronizer? | A reset synchronizer is a circuit that uses two flip-flops on the reset deassertion path to ensure that the reset signal | The answer accurately describes the function of a reset synchronizer as stated i |
| q14 | faithful | FAIL (refused) | What energy does the hash module consume? | I don't know based on the provided documents. | - |
| q15 | faithful | PASS | What is at register offset 0x04? | At register offset 0x04, there is the STATUS register, which is read-only (RO) and indicates the status of the module, w | The ANSWER accurately describes the STATUS register at offset 0x04 as read-only  |
| q16 | refusal | PASS | Tell me about NVIDIA H100 pricing | I don't know based on the provided documents. | - |
