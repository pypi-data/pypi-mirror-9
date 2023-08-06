class Colorizer(): # Uses ANSI escape characters to stylize a string. This is not an interesting class but it saves code!

    def __init__(self):
        self

    def String(self, string, color, styling): # Uses ANSI escape sequences for color and style.
        attr = []
        # Foreground colors, default is white (37).
        if color == "red": attr.append('31')
        if color == "green": attr.append('32')
        if color == "yellow": attr.append('33')
        if color == "blue": attr.append('34')
        if color == "magenta": attr.append('35')
        if color == "cyan": attr.append('36')
        if color == "white": attr.append('37')

        # Style options, default is normal display(0).
        if styling == "bold": attr.append('1')
        if styling == "underline": attr.append('4')

        return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

    def RedBold(self, string):
        return self.String(string, "red", "bold" )

    def RedUnderline(self, string):
        return self.String(string, "red", "underline")

    def Red(self, string):
        return self.String(string, "red", "normal")

    def GreenBold(self, string):
        return self.String(string, "green", "bold")

    def GreenUnderline(self, string):
        return self.String(string, "green", "underline")

    def Green(self, string):
        return self.String(string, "green", "normal")

    def YellowBold(self, string):
        return self.String(string, "yellow", "bold")

    def YellowUnderline(self, string):
        return self.String(string, "yellow", "underline")

    def Yellow(self, string):
        return self.String(string, "yellow", "normal")

    def BlueBold(self, string):
        return self.String(string, "blue", "bold")

    def BlueUnderline(self, string):
        return self.String(string, "blue", "underline")

    def Blue(self, string):
        return self.String(string, "blue", "normal")

    def MagentaBold(self, string):
        return self.String(string, "magenta", "bold")

    def MagentaUnderline(self, string):
        return self.String(string, "magenta", "underline")

    def Magenta(self, string):
        return self.String(string, "magenta", "normal")

    def CyanBold(self, string):
        return self.String(string, "cyan", "bold")

    def CyanUnderline(self, string):
        return self.String(string, "cyan", "underline")

    def Cyan(self, string):
        return self.String(string, "cyan", "normal")

    def WhiteBold(self, string):
        return self.String(string, "white", "bold")

    def WhiteUnderline(self, string):
        return self.String(string, "white", "underline")

    def ColorEngine(self, string, color_code="w"):
        # Just another means to color items. Implement this for menus
        # that you want to give a color option. Works with ParameterPrompt.
        # Should return an uncolored string if there's an error.
        
        nstring = string.lower()
        
        if color_code == "rb": nstring = self.RedBold(string)
        if color_code == "ru": nstring = self.RedUnderline(string)
        if color_code == "r": nstring = self.Red(string)

        if color_code == "gb": nstring = self.GreenBold(string)
        if color_code == "gu": nstring = self.GreenUnderline(string)
        if color_code == "g": nstring = self.Green(string)

        if color_code == "yb": nstring = self.YellowBold(string)
        if color_code == "yu": nstring = self.YellowUnderline(string)
        if color_code == "y": nstring = self.Yellow(string)

        if color_code == "bb": nstring = self.BlueBold(string)
        if color_code == "bu": nstring = self.BlueUnderline(string)
        if color_code == "b": nstring = self.Blue(string)

        if color_code == "mb": nstring = self.MagentaBold(string)
        if color_code == "mu": nstring = self.MagentaUnderline(string)
        if color_code == "m": nstring = self.Magenta(string)

        if color_code == "cb": nstring = self.CyanBold(string)
        if color_code == "cu": nstring = self.CyanUnderline(string)
        if color_code == "c": nstring = self.Cyan(string)

        if color_code == "wb": nstring = self.WhiteBold(string)
        if color_code == "wu": nstring = self.WhiteUnderline(string)

        return nstring

