# Market Making Competition

This repository contains the skeleton code for the Market Making Competition.

## Introduction

Market making is a trading strategy that involves providing liquidity to the market by simultaneously offering to buy and sell a particular asset. Market makers profit from the bid-ask spread, which is the difference between the price at which they are willing to buy (bid) and the price at which they are willing to sell (ask). By continuously quoting prices and executing trades, market makers help to ensure that there is always a buyer or seller available, thus enhancing market efficiency and stability.

## Story

Imagine you are a leading trading firm specializing in market making for a single stock. Your goal is to develop a robust market-making strategy that maximizes your profits while managing risks. You will implement your strategy in the `MarketMaker` class and test it using a simulation environment provided in this repository.

## Instructions

1. **Create Your Strategy**
    - Implement your strategy in the `MarketMaker` class located in `maker.py`.


2. **Implement the `update` Method**
    - In the `MarketMaker` class, you need to implement the `update` method:
        ```python
        def update(self, prevBuy, prevSell) -> Tuple[float, int, float, int]:
            pass
        ```
    - **Inputs:**
        - `prevBuy` (float): The price at which the simulated market willing to buy the day before.
        - `prevSell` (float): The price at which the simulated market willing to sell the day before.
    - **Outputs:**
        - A tuple containing:
        - `newBid` (float): The new bid price you are willing to offer.
        - `bidSize` (int): The size of the bid order.
        - `newAsk` (float): The new ask price you are willing to offer.
        - `askSize` (int): The size of the ask order.

3. **Run the Simulation**
    - Use your strategy in `main.py` to run the simulation.

4. **Setup Environment**
    - Create a virtual environment and install the required dependencies:
      ```sh
      python -m venv env
      source env/bin/activate  # On Windows use `env\Scripts\activate`
      pip install -r requirements.txt
      ```

4. **Execute the Simulation**
    - Run the simulation using:
      ```sh
      python main.py
      ```

## Logs

- The log for each run is stored in the `log` directory.

Happy coding and good luck with the competition!