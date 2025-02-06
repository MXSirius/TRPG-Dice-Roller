"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import random
import re


class DiceRoller:
    """
    骰点工具类，用于模拟掷骰子游戏中的骰点行为。该类支持多种掷骰表达式，并能够根据不同的难度等级和需求值进行检定。

    主要功能包括：
    - 解析并执行标准的掷骰表达式（如 "2d6+3"）。
    - 根据不同的难度等级（普通、困难、极难）和需求值判断掷骰结果。
    - 支持快速掷骰、重复掷骰等多种掷骰方式。
    - 处理1d100的特殊规则，包括大成功和大失败的判定。

    主要方法：
    - `roll_dice`: 根据传入的骰子表达式投掷骰子，返回骰点结果和骰点详情。
    - `check_success`: 根据不同的难度等级判定是否成功。
    - `evaluate_expression`: 分析掷骰表达式并做出相应动作，输出投点结果。
    - `quick_roll`: 快速掷骰子并返回结果。
    - `repeat_roll`: 判别重复检定指令并执行相应的掷骰操作。
    - `_execute_rolls`: 根据指定的次数和掷骰表达式，执行重复掷骰操作并返回结果。

    注意事项：
    - 掷骰表达式格式为 "XdY+Z"，其中 X 是骰子数量，Y 是骰子面数，Z 是修正值（可选）。
    - 难度等级选项包括：普通（默认）、困难（-h）、极难（-e）。
    - 孤注一掷选项为 -g，失败时一律视为大失败。
    - 需求值检定格式为 "target/dice_expression"，其中 target 是需求值，dice_expression 是掷骰表达式。
    - 重复掷骰指令格式为 ".m -n expression" 或 ".d/.t expression"，其中 n 是重复次数，expression 是掷骰表达式。
    """

    def roll_dice(self, dice_expression):
        """
        根据传入的骰子表达式投掷骰子，返回骰点结果和骰点详情

        Args:
            dice_expression (str): 符合骰子表达式格式的字符串，例如 "2d6+3"

        Raises:
            ValueError: 如果传入的骰子表达式格式不正确或无法解析

        Returns:
            tuple[int, str]: 返回一个元组，第一个元素是骰点结果（整数），第二个元素是骰点详情（字符串）
        """

        # 输入验证
        match = re.match(r'(\d*)d(\d+)([+-]\d+)?', dice_expression)
        if not match:
            raise ValueError("无效的表达式！")

        # 骰子的数量，至少投掷一个骰子
        num_dice = int(match.group(1)) if match.group(1) else 1
        # 骰子的面数
        dice_type = int(match.group(2))
        # 骰子的修正值，默认为 0
        modifier = int(match.group(3)) if match.group(3) else 0

        # rolls 为每个骰子投出的点数
        rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
        # total 为所有骰子的点数加上修正值
        total = sum(rolls) + modifier

        # 返回骰点结果和骰点详情
        roll_details = '+'.join(map(str, rolls))
        if modifier != 0:
            roll_details += f'{match.group(3)}'
        return total, roll_details

    def check_success(self, target, total, lvl):
        """
        根据不同的难度等级判定是否成功

        Args:
            target (int): 需求值，即目标点数。
            total (int): 实际投出的点数总和。
            lvl (str): 难度等级，可选值为 'h'（困难）、'e'（极难）或其他字符串表示默认难度。

        Returns:
            tuple: 包含两个元素的元组，第一个元素是布尔值，表示是否成功；第二个元素是通过检定的阈值。
        """
        # 困难难度：投出的点数需要小于等于需求值的一半（向下取整）才能检定通过。
        if lvl == 'h':
            threshold = target // 2
        # 极难难度：投出的点数需要小于等于需求值的1/5（向下取整）才能检定通过。
        elif lvl == 'e':
            threshold = target // 5
        # 默认难度：投出的点数只需要小于等于需求值即通过检定。
        else:
            threshold = target

        success = total <= threshold
        return success, threshold

    def evaluate_expression(self, expression):
        """
        分析掷骰表达式并做出相应动作，输出投点结果

        Args:
            expression (str): 掷骰表达式，例如 "1d20+5 -g" 或 "10/1d20+5 -h"。
                支持的选项有：
                - "-g"：表示孤注一掷
                - "-h"：表示困难难度
                - "-e"：表示极难难度
                - "/"：用于分隔需求值和掷骰表达式，如 "10/1d20+5"

        Returns:
            str: 投点结果，包括投点详情、总点数以及根据需求值和难度等级判断的结果。
                如果掷的是1d100，还会包含大成功或大失败的信息。
                如果表达式解析或计算过程中出现错误，返回错误信息。
        """
        try:
            # 初始化结果变量
            roll_result = ""

            # 处理选项
            options = {'-g': False, '-h': False, '-e': False}
            for option in options:
                if option in expression:
                    options[option] = True
                    expression = expression.replace(option, '').strip()

            # 难度分级
            lvl_map = {'n': '', 'h': '困难', 'e': '极难'}
            lvl = 'h' if options['-h'] else 'e' if options['-e'] else 'n'

            # 需求值检定
            if '/' in expression:
                target, dice_expression = expression.split('/')
                target = int(target)
            else:
                target, dice_expression = None, expression

            total, roll_details = self.roll_dice(dice_expression.strip())

            # 百面骰独有的大成功与大失败机制
            if '1d100' in dice_expression:
                if total == 1:
                    return f"{dice_expression.strip()}: {roll_details}={total}, 大成功！"
                if total >= 96:
                    return f"{dice_expression.strip()}: {roll_details}={total}, 大失败！"

            # 根据骰点结果和需求值进行判断
            if target is not None:
                success, threshold = self.check_success(target, total, lvl)
                if success:
                    roll_result = f"{total}<={threshold}, {lvl_map[lvl]}检定通过！"
                else:
                    if options['-g']:
                        roll_result = f"{total}>{threshold}, {lvl_map[lvl]}孤注一掷失败，视为大失败！"
                    else:
                        roll_result = f"{total}>{threshold}, {lvl_map[lvl]}检定失败！"
            else:
                roll_result = f"{total}"

            return f"{dice_expression.strip()}: {roll_details}={total}, {roll_result}"

        except Exception as e:
            return f"错误：{str(e)}"

    def quick_roll(self, command):
        """
        快速掷骰子并返回结果。

        Args:
            command (str): 用户输入的命令字符串，格式为 ".r [骰子面数]"。例如 ".r 20" 表示掷一个20面骰子，默认为100面骰子。

        Raises:
            ValueError: 当输入的命令格式无效时抛出此异常。

        Returns:
            str: 掷骰子的结果字符串，格式为 "1dX: Y=Z"，其中 X 是骰子面数，Y 是详细的掷骰子过程，Z 是总和。
                如果发生错误，则返回错误信息字符串，格式为 "错误：{错误信息}"。
        """
        try:
            match = re.match(r'\.r\s*(\d+)?', command)
            if match:
                dice_type = int(match.group(1)) if match.group(1) else 100
                dice_expression = f"1d{dice_type}"
                total, roll_details = self.roll_dice(dice_expression)
                return f"{dice_expression}: {roll_details}={total}"

            raise ValueError("无效的表达式！")

        except Exception as e:
            return f"错误：{str(e)}"

    def repeat_roll(self, command, expression=None):
        """
        判别重复检定指令并执行相应的掷骰操作。

        Args:
            command (str): 用户输入的命令字符串。支持以下格式：
                - ".m -n expression"：表示进行 n 次重复掷骰，expression 为掷骰表达式。
                - ".d expression"：表示进行 2 次重复掷骰（难度检定），expression 为掷骰表达式。
                - ".t expression"：表示进行 3 次重复掷骰（团队检定），expression 为掷骰表达式。
            expression (str, optional): 如果在命令中未提供掷骰表达式，则使用此参数作为默认表达式。Defaults to None.

        Raises:
            ValueError: 当输入的命令格式无效时抛出此异常。

        Returns:
            str: 执行重复掷骰的结果字符串。如果发生错误，则返回错误信息字符串，格式为 "错误：{错误信息}"。
        """

        try:
            # m型模式：.m -n expression
            m_match = re.match(r'\.m\s+-(\d+)\s+(.+)', command)
            if m_match:
                times = int(m_match.group(1))
                expression = m_match.group(2)
                return self._execute_rolls(times, expression)

            # d/t型模式：.d/.t expression
            dt_match = re.match(r'\.(d|t)\s+(.+)', command)
            if dt_match:
                repeat_type = dt_match.group(1)
                times = 2 if repeat_type == 'd' else 3
                expression = dt_match.group(2)
                return self._execute_rolls(times, expression)

            raise ValueError("无效的重复检定指令！")

        except Exception as e:
            return f"错误：{str(e)}"

    def _execute_rolls(self, times, expression):
        """
        根据指定的次数和掷骰表达式，执行重复掷骰操作并返回结果。

        Args:
            times (int): 重复掷骰的次数。
            expression (str): 掷骰表达式，例如 "2d6+3"。

        Returns:
            str: 多次掷骰的结果字符串，每行显示一次掷骰的结果，格式为 "第 X 次 -> 结果"。
        """
        results = []
        for i in range(times):
            roll_result = self.evaluate_expression(expression)
            results.append(f"第 {i+1} 次 -> {roll_result}")
        return "\n".join(results)


if __name__ == '__main__':
    roller = DiceRoller()
    print("欢迎来到COC的世界。你，和你的同伴，将决定整个世界的命运！")
    print("- 输入'.r'来立即投掷一个百面骰，或者使用'.r n'来投掷一个 n 面骰。")
    print("- 输入掷骰表达式，如 '3d6+2'，表示投掷 3 个 6 面骰并加上 2。")
    print("- 输入需求值检定，如 '10/3d6+2'，表示投掷 3 个 6 面骰并加上 2，判断是否小于等于 10。")
    print("- 输入'-h'来进行困难难度检定，'-e'来进行极难难度检定，'-g'来进行孤注一掷检定。")
    print("- 输入'.q'来退出程序。", end='\n\n')

    while True:
        expr = input("请输入掷骰表达式：\n")
        # 退出指令
        if expr.lower().strip() == '.q':
            print("再见，愿你在梦中也能保持清醒。")
            break
        # 快速 roll 点指令
        elif expr.startswith('.r'):
            result = roller.quick_roll(expr)
        # 快速重复检定指令
        elif expr.startswith(('.d', '.t', '.m')):
            result = roller.repeat_roll(expr, None)
        # 掷骰表达式
        else:
            result = roller.evaluate_expression(expr)
        print(result, end='\n\n')
