# How to Test Your Gateway's Unique ID

## 🎯 Purpose

This test helps verify that the ATW-MBS-02 gateway unique ID is:
1. **Stable** - Returns the same value each time
2. **Unique** - Different for each gateway

By sharing your results, you help validate the solution for all users!

## 📋 Prerequisites

1. **Python environment** with `uv` installed
2. **Network access** to your ATW-MBS-02 gateway
3. **Modbus TCP** enabled on the gateway

## 🚀 Quick Start

### Step 1: Clone or Download the Repository

```bash
git clone https://github.com/alepee/hitachi-yutaki-modus-data-extractor.git
cd hitachi-yutaki-modus-data-extractor
```

### Step 2: Run the Test Script

#### On Linux / macOS:

```bash
./scripts/get_unique_id.sh
```

When prompted, enter your gateway's IP address (press Enter for default `192.168.0.4`):
```
Enter your gateway IP address [192.168.0.4]: 
```

#### On Windows:

```cmd
scripts\get_unique_id.bat
```

When prompted, enter your gateway's IP address (press Enter for default `192.168.0.4`):
```
Enter your gateway IP address [192.168.0.4]: 
```

### Step 3: Share Your Results

Copy the **entire output** from your terminal and post it in the [GitHub discussion/issue](link_to_issue).

**Important**: Please include:
- Your unique ID (e.g., `3846-103-56`)
- Your gateway model (if different from ATW-MBS-02)
- Any error messages if the test fails

## 📊 Example Output

```
======================================================================
Hitachi ATW-MBS-02 Gateway - Unique ID Reader
======================================================================

Reading unique ID from gateway...

======================================================================
Gateway Unique ID Retrieval
======================================================================
Target: 192.168.0.4

✅ Unique ID (decimal): 3846-103-56
✅ Unique ID (hex):     0F06:0067:0038

======================================================================

✅ Success! Please share the output above on GitHub.
```

## 🔍 What We're Looking For

### Good Signs ✅
- ✅ You get a unique ID like `3846-103-56`
- ✅ The ID is the same when you run the script multiple times
- ✅ The ID is **different** from other users' IDs

### Bad Signs ⚠️
- ❌ Connection errors (check IP and network)
- ❌ Different ID on each run (unstable)
- ❌ Same ID as another user (not unique)

## 🐛 Troubleshooting

### Error: "Failed to connect"
- Verify your gateway IP address (double-check the IP you entered)
- Check that the gateway is powered on and connected to your network
- Ensure Modbus TCP is enabled on the gateway (usually port 502)
- Try pinging the gateway: `ping 192.168.0.4`

### Error: "Module not found"
Make sure you have `uv` installed:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or on Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then run:
```bash
uv sync
```

### Error: "Read error"
- The gateway may not support Input Registers at addresses 0-2
- Try running the extended diagnostic script: `python scan_input_registers.py --start 0 --end 10`

## 🤝 Contributing

Your test results help validate the solution for Home Assistant integration!

### What to Share

Please post in the GitHub issue/discussion:

```
**Gateway Model**: ATW-MBS-02
**Unique ID (decimal)**: 3846-103-56
**Unique ID (hex)**: 0F06:0067:0038
**Test Date**: 2026-01-24
**Stability**: ✅ Same ID across 3 test runs
**Additional Notes**: Works perfectly, no issues
```

## 📚 Technical Details

The unique ID is read from **Input Registers 1-3** (Modbus addresses 0-2) using function code 04 (Read Input Registers).

These registers appear to contain:
- Register 1 (addr 0): Firmware version or hardware ID
- Register 2 (addr 1): Serial number part 1
- Register 3 (addr 2): Serial number part 2

The combination creates a stable, unique identifier suitable for Home Assistant's `unique_id` requirement.

## 📞 Need Help?

- Open an issue on GitHub
- Check existing discussions for similar problems
- Consult [UNIQUE_ID_SOLUTION.md](./UNIQUE_ID_SOLUTION.md) for detailed technical information

## ⚖️ License

Same as the main project (check repository root).
