# Graph Visualizer

## Installation

To get started with Graph Visualizer, follow these steps:

```bash
git clone https://github.com/Hihthei/Graph-visualizer

cd Graph-visualizer
```

### Install Dependencies

- Using poetry:

   ```bash
   pip install poetry
   ```

   ```bash
   poetry install
   ```

   ```bash
   poetry shell
   ```

   To find your interpretor:

   ```bash
   poetry env info
   ```

   And then choose the excutable path

- Using pyenv:

    - Windows:
        https://github.com/pyenv-win/pyenv-win

    - Unix:
        https://github.com/pyenv/pyenv

   ```bash
   pyenv install 3.12.4
   ```

   ```bash
   pyenv local 3.12.4
   ```

   ```bash
   pip install networkx

   pip install pyqt6
   ```

## Overview

Graph Visualizer is an interactive tool designed to create, manipulate, and visualize graphs.
This application provides a user-friendly interface to perform common graph operations and visualize algorithms.

## Features

- **UI-Friendly Graph Manipulation**: Add, remove, and link nodes interactively.
- **Graph Algorithms**:
  - Breadth-First Search (BFS)
  - Depth-First Search (DFS)
- **Random Graph Generation**: Automatically create a fonctionnal graph.
- **Dynamic Visualization**: Step-by-step visualization of graph algorithms.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
