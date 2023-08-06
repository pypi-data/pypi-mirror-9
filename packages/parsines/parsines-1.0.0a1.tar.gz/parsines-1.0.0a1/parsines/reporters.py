
from json import dumps


def json_report(ines_file):
    print(dumps(ines_file.header.__dict__, indent=2))


def plain_text_report(ines_file):
    ines_header = ines_file.header
    s = ""
    s += "iNES ROM File\n"
    s += "-------------\n"
    s += "ROM Version           = %s\n" % ines_header.version
    s += "PRG ROM Size          = %s KB or %s B\n" % (ines_header.prg_rom_size, ines_header.prg_rom_size * 1024)
    s += "CHR ROM Size          = %s KB or %s B\n" % (ines_header.chr_rom_size, ines_header.chr_rom_size * 1024)
    s += "CHR RAM               = %s\n" % yesno(ines_header.uses_chr_ram)
    s += "Mapper ID             = %s\n" % ines_header.mapper_id

    s += "Mirroring             = "
    if ines_header.mirroring == ines_header.VERTICAL_MIRRORING:
        s += "vertical\n"
    else:
        s += "horizontal\n"

    s += "Battery-backed ram    = "
    if ines_header.has_battery_backed_ram:
        s += "YES at $6000 to $7FFF\n"
    else:
        s += "NO \n"

    s += "Trainer               = "
    if ines_header.has_trainer:
        s += "YES at $7000 to $71FF\n"
    else:
        s += "NO\n"

    s += "4-screen VRAM Layout  = %s\n" % yesno(ines_header.has_4_screen_vram_layout)
    s += "VS System Cartridge   = %s\n" % yesno(ines_header.is_vs_system_cartridge)
    s += "8KB RAM Banks         = %s\n" % ines_header.ram_banks

    s += "Color encoding system = "
    if ines_header.color_encoding_system == ines_header.PAL:
        s += "PAL\n"
    else:
        s += "NTSC\n"

    print(s)


def yesno(b):
    return "YES" if b else "NO"
