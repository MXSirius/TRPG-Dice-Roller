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

"""
★ TRPG 跑团掷骰模拟器 ★

1. 基础模块
    输入：掷骰表达式，如 "3d6+2"，表示投掷 3 个 6 面骰并加上 2。
    需求值检定：如 "10/3d6+2"，表示投掷 3 个 6 面骰并加上 2，判断是否小于等于 10。
    检定结果输出：根据骰点结果比较需求值的大小，输出是否成功。成功规则请看下述。

2. 快速roll点
    ".r"：立即投掷一个百面骰，输出结果。
    ".r n"：立即投掷一个 n 面骰，输出结果。
    注：快捷指令不进行检定，只输出骰点结果。

3. 快速重复检定
    ".d"：连续进行两次相同的检定，分别按行输出两次的检定结果。
    ".t"：连续进行三次相同的检定，分别按行输出三次的检定结果。
    ".m -n"：连续进行 n 次相同的检定，分别按行输出 n 次的检定结果。

4. 成功判断
    常规难度：投出的点数只需要小于等于需求值即通过检定。默认即为此情况。
    困难难度：投出的点数需要小于等于需求值的一半（向下取整）才能检定通过。对应指令"-h"。
    极难难度：投出的点数需要小于等于需求值的1/5（向下取整）才能检定通过。对应指令"-e"。
    大成功：投掷百面骰时，骰出1即为大成功。输出"大成功！"。
    大失败：投掷百面骰时，骰出96-100即为大失败。输出"大失败！"。
    孤注一掷：在原有难度判断的基础上，只要失败了就一律视为大失败。对应指令"-g"。

5. 示例输入输出
    "3d6+2" -> "3d6+2: 4+5+6+2=17"
    ".d 1d6" -> "第 1 次 -> 1d6: 3=3"
                "第 2 次 -> 1d6: 6=6"
    "20/1d100+2" -> "1d100+2: 15+2=17, 17<=20, 检定通过！"
    "40/1d100+2 -h" -> "1d100+2: 15+2=17, 17<=20, 困难检定通过！"
    "50/1d100+2 -e" -> "1d100+2: 15+2=17, 17>10, 极难检定失败！"
    "20/1d100 -g" -> "1d100: 50=50, 50>20, 孤注一掷失败，视为大失败！"
    "100/1d100 -e -g" -> "1d100: 50=50, 50>20, 极难孤注一掷失败，视为大失败！"
    ".r" -> "1d100: 50=50"
    ".r 20" -> "1d20: 10=10"
    ".m -2 20/1d100+2 -h" -> "第 1 次 -> 1d100+2: 15+2=17, 17<=20, 困难检定通过！"
                             "第 2 次 -> 1d100+2: 75+2=77, 77>20, 困难检定失败！"
"""

import random
import re


class DiceRoller:

    # 根据传入的表达式投掷骰子，返回骰点结果和骰点详情
    def roll_dice(self, dice_expression):
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

    # 根据不同的难度等级判定是否成功
    def check_success(self, target, total, difficulty):
        # 困难难度：投出的点数需要小于等于需求值的一半（向下取整）才能检定通过。
        if difficulty == 'h':
            threshold = target // 2
        # 极难难度：投出的点数需要小于等于需求值的1/5（向下取整）才能检定通过。
        elif difficulty == 'e':
            threshold = target // 5
        # 默认难度：投出的点数只需要小于等于需求值即通过检定。
        else:
            threshold = target

        success = total <= threshold
        return success, threshold

    # 分析掷骰表达式并做出相应动作，输出投点结果
    def evaluate_expression(self, expression):
        try:
            # 孤注一掷
            gamble = '-g' in expression
            if gamble:
                expression = expression.replace(' -g', '')

            # 难度分级
            difficulty = 'n'
            if '-h' in expression:
                difficulty = 'h'
                expression = expression.replace(' -h', '')
            elif '-e' in expression:
                difficulty = 'e'
                expression = expression.replace(' -e', '')

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
                elif total >= 96:
                    return f"{dice_expression.strip()}: {roll_details}={total}, 大失败！"

            # 根据骰点结果和需求值进行判断
            if target is not None:
                success, threshold = self.check_success(
                    target, total, difficulty)
                difficulty_str = ""
                if difficulty == 'h':
                    difficulty_str = "困难"
                elif difficulty == 'e':
                    difficulty_str = "极难"

                if success:
                    result = f"{total}<={threshold}, {difficulty_str}检定通过！"
                else:
                    if gamble:
                        result = f"{total}>{threshold}, {difficulty_str}孤注一掷失败，视为大失败！"
                    else:
                        result = f"{total}>{threshold}, {difficulty_str}检定失败！"

            else:
                result = f"{total}"

            return f"{dice_expression.strip()}: {roll_details}={total}, {result}"
        except Exception as e:
            return f"错误：{str(e)}"

    # 快速 roll 点
    def quick_roll(self, command):
        try:
            match = re.match(r'\.r\s*(\d+)?', command)
            if match:
                dice_type = int(match.group(1)) if match.group(1) else 100
                dice_expression = f"1d{dice_type}"
                total, roll_details = self.roll_dice(dice_expression)
                return f"{dice_expression}: {roll_details}={total}"
            else:
                raise ValueError("无效的表达式！")
        except Exception as e:
            return f"错误：{str(e)}"

    def repeat_roll(self, command, expression=None):
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
        """执行指定次数的掷骰"""
        results = []
        for i in range(times):
            result = self.evaluate_expression(expression)
            results.append(f"第 {i+1} 次 -> {result}")
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
