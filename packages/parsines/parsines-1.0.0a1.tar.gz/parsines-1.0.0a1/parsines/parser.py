
def ord_or_int(v):
    try:
        return ord(v)
    except TypeError:
        return int(v)


class INESHeader(object):
    HORIZONTAL_MIRRORING = "HORIZONTAL"
    VERTICAL_MIRRORING = "VERTICAL"
    PAL = "PAL"
    NTSC = "NTSC"
    VERSION_ARCHAIC = "archaic"
    VERSION_INES_0_7 = "INES 0.7"
    VERSION_INES = "INES"
    VERSION_NES_2_0 = "NES 2.0"

    def __init__(self):
        self.prg_rom_size = 0
        self.chr_rom_size = 0
        self.uses_chr_ram = False
        self.mapper_id = 0
        self.mirroring = self.HORIZONTAL_MIRRORING
        self.has_battery_backed_ram = False
        self.has_trainer = False
        self.has_4_screen_vram_layout = False
        self.is_vs_system_cartridge = False
        self.ram_banks = 1
        self.color_encoding_system = self.NTSC
        self.version = INESHeader.VERSION_INES


class INESFile(object):

    def __init__(self):
        self.header = None
        self.prg_rom = None
        self.chr_rom = None
        self.inst_rom = None
        self.prom = None


class INESFileParser(object):

    class InvalidHeaderConstant(Exception):
        pass

    def parse(self, file_object):
        header = self._parse_header(file_object)
        ines_file = INESFile()
        ines_file.header = header
        return ines_file

    def _assert_header_constant(self, header_bytes):
        if header_bytes[0:4] != b'\x4E\x45\x53\x1A':
            raise self.InvalidHeaderConstant()

    def _parse_header(self, file_object):
        header_bytes = file_object.read(16)
        self._assert_header_constant(header_bytes)
        header = INESHeader()
        header.prg_rom_size = self._get_prg_rom_size(header_bytes)
        header.chr_rom_size = self._get_chr_rom_size(header_bytes)
        header.uses_chr_ram = header.chr_rom_size == 0
        header.mapper_id = self._get_mapper_id(header_bytes)
        header.mirroring = self._get_mirroring(header_bytes)
        header.has_battery_backed_ram = self._get_has_battery_backed_ram(header_bytes)
        header.has_trainer = self._get_has_trainer(header_bytes)
        header.has_4_screen_vram_layout = self._get_has_4_screen_vram_layout(header_bytes)
        header.ram_banks = self._get_ram_banks(header_bytes)
        header.color_encoding_system = self._get_color_encoding_system(header_bytes)
        header.version = self._get_ROM_version(header_bytes)
        return header

    def _get_prg_rom_size(self, header_bytes):
        return ord_or_int(header_bytes[4]) * 16

    def _get_chr_rom_size(self, header_bytes):
        return ord_or_int(header_bytes[5]) * 8

    def _get_mapper_id(self, header_bytes):
        low_nibble = ord_or_int(header_bytes[6]) >> 4
        high_nibble = ord_or_int(header_bytes[7]) >> 4
        return int(format(high_nibble, '04b') + format(low_nibble, '04b'), 2)

    def _get_mirroring(self, header_bytes):
        if ord_or_int(header_bytes[6]) & (1 << 0):
            return INESHeader.VERTICAL_MIRRORING
        else:
            return INESHeader.HORIZONTAL_MIRRORING

    def _get_has_battery_backed_ram(self, header_bytes):
        return bool(ord_or_int(header_bytes[6]) & (1 << 1))

    def _get_has_trainer(self, header_bytes):
        return bool(ord_or_int(header_bytes[6]) & (1 << 2))

    def _get_has_4_screen_vram_layout(self, header_bytes):
        return bool(ord_or_int(header_bytes[6]) & (1 << 3))

    def _get_is_vs_system_cartridge(self, header_bytes):
        return bool(ord_or_int(header_bytes[7]) & (1 << 0))

    def _get_ram_banks(self, header_bytes):
        if ord_or_int(header_bytes[8]) == 0:
            return 1
        else:
            return ord_or_int(header_bytes[8])

    def _get_color_encoding_system(self, header_bytes):
        if ord_or_int(header_bytes[9]) & (1 << 0):
            return INESHeader.PAL
        else:
            return INESHeader.NTSC

    def _get_ROM_version(self, header_bytes):
        v = ord_or_int(header_bytes[7]) & 0x0C
        if v == 0x08:
            return INESHeader.VERSION_NES_2_0
        elif v == 0x00 and all([ord_or_int(b) == 0 for b in header_bytes[12:15]]):
            return INESHeader.VERSION_INES
        else:
            return INESHeader.VERSION_ARCHAIC

