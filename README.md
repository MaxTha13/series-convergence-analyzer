# Series Convergence Analyzer (D'Alembert's Ratio Test)

A Python application with a Graphical User Interface (GUI) built using `tkinter` and `sympy`. This tool allows users to input mathematical series and automatically tests for convergence using **D'Alembert's Ratio Test**.

## Features

- **Visual Input**: Supports complex mathematical notation like superscripts ($n^2$), roots ($\sqrt{n}, \sqrt[3]{n}$), and factorials ($n!$).
- **Automatic Calculation**: Parses the visual input into Python expressions.
- **Symbolic Math**: Uses `sympy` to calculate the limit $\lim_{n \to \infty} |\frac{a_{n+1}}{a_n}|$ symbolically.
- **Clear Results**: Displays the general term, the ratio, the limit value, and the final conclusion (Convergent/Divergent/Inconclusive).

## Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/MaxTha13/series-convergence-analyzer.git](https://github.com/MaxTha13/series-convergence-analyzer.git)
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Enter the numerator and denominator in the input fields.
3. Use the buttons to add special symbols (powers, roots, factorials).
4. Click "Analyze series" to see the results.