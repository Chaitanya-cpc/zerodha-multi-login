# 🔒 Safe Sudo Configuration for Shutdown

This guide will help you safely configure passwordless sudo for the shutdown command.

## ⚠️ Security Note

We're configuring sudo to allow ONLY the `/sbin/shutdown` command without a password. This is safer than giving full sudo access.

## 🚀 Quick Setup (Recommended)

Run the helper script:

```bash
bash scripts/configure_shutdown_sudo.sh
```

This script will:
1. Guide you through the process
2. Open `visudo` (the safe way to edit sudoers)
3. Help you add the configuration
4. Verify it works

## 📝 Manual Setup

If you prefer to do it manually:

### Step 1: Open sudoers file safely

```bash
sudo visudo
```

**Important:** Always use `visudo` - it validates the syntax before saving, preventing system lockout.

### Step 2: Add the configuration line

Scroll to the end of the file and add this line:

```
chaitanya ALL=(ALL) NOPASSWD: /sbin/shutdown
```

**Replace `chaitanya` with your username if different.**

### Step 3: Save and exit

- **Nano editor:** Press `Ctrl+X`, then `Y`, then `Enter`
- **Vim editor:** Press `Esc`, type `:wq`, then `Enter`

### Step 4: Verify it works

Test the configuration:

```bash
# This should work without asking for password
sudo -n shutdown -h +1

# Cancel the test shutdown immediately
sudo shutdown -c
```

If it works without asking for a password, you're all set! ✅

## 🔍 Troubleshooting

### Issue: "visudo: command not found"

**Solution:** Install sudo:
```bash
sudo apt install sudo  # Ubuntu/Debian
```

### Issue: "You are not in the sudoers file"

**Solution:** Your user needs sudo privileges. Contact your system administrator or add yourself to the sudo group:
```bash
su -  # Switch to root
usermod -aG sudo chaitanya
```

### Issue: Syntax error in sudoers

**Solution:** If you get a syntax error, run:
```bash
sudo visudo -c
```

This will check the syntax and show you where the error is.

## ✅ Verification

After configuration, verify:

```bash
# Check sudo rules
sudo -l | grep shutdown

# Test shutdown (will schedule for 1 minute - cancel immediately!)
sudo -n shutdown -h +1
sudo shutdown -c
```

## 🛡️ Security Best Practices

1. ✅ **Only allow specific command** - We're only allowing `/sbin/shutdown`, not all commands
2. ✅ **Use visudo** - Always use `visudo` to edit sudoers (validates syntax)
3. ✅ **Test carefully** - Always test with a delayed shutdown first (`+1` = 1 minute delay)
4. ✅ **Keep backups** - The sudoers file is backed up automatically by visudo

## 📋 What This Configuration Does

- Allows user `chaitanya` to run `/sbin/shutdown` without password
- Does NOT give full sudo access
- Only works for the shutdown command
- Still requires sudo (just no password prompt)

## 🔄 Removing the Configuration

If you want to remove this later:

```bash
sudo visudo
# Remove or comment out the line:
# chaitanya ALL=(ALL) NOPASSWD: /sbin/shutdown
```

---

**Setup complete!** Your shutdown cron job will now work without password prompts.
