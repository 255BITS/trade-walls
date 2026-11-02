# TradeWalls.near

TradeWalls is a cryptocurrency trading tool that allows users to plan their trades in advance and have an autonomous agent execute them later. It utilizes a trading strategy aimed at optimizing the ownership of a chosen asset.

## The Problem

Cryptocurrency markets are known for their volatility, making it challenging for individuals to determine the optimal times to buy or sell. Many people fall victim to hype cycles, often buying at the wrong time and suffering financial losses as a result.

## The Solution

TradeWalls provides a structured approach to trading. Users can plan their trades in advance, focusing on accumulating valuable assets over time. The TradeWalls strategy involves selecting two cryptocurrency pairs that the user believes have long-term potential. By defining a set of trading rules, known as "walls," TradeWalls helps users determine when to swap one asset for the other, gradually increasing their holdings in the desired cryptocurrency.

TradeWalls runs locally on your infrastructure keeping your walls private.

## How It Works

1. Choose two cryptocurrency pairs you believe in and want to accumulate. Refer to them by their coingecko ids (in the url for coingecko. Ex: coingecko. com/en/coins/near)
2. Define a set of trading rules, or "walls," specifying the prices at which you want to buy or sell each asset.
3. The autonomous TradeWalls agent monitors the market, alerting you when the planned trades become possible.
4. Safely store your coins when not actively trading to ensure the security of your assets.
5. Let the agent monitor the markets so you can build.

## Interacting with TradeWalls

TradeWalls provides an interface powered by the AI Nexus on BOS. Users can interact with the LLM to suggest and create trading walls based on their preferences and market insights. The LLM assists in setting up trading strategies, allowing users to define their desired trading parameters. Note, please use GPT-4 as other models don't reliably return json.

## Considerations

- TradeWalls is a tool that requires technical understanding and should be used by individuals comfortable with cryptocurrency trading concepts.
- Users should carefully consider their trading strategies and understand the potential risks involved.
- It is important to securely store coins when not actively trading to ensure the safety of your assets.

## Potential Impact

TradeWalls has the potential to change the way cryptocurrency enthusiasts approach long-term accumulation. By providing a structured and automated trading strategy, TradeWalls empowers users to gradually increase their holdings in the cryptocurrencies they believe in. This tool can help users navigate the volatile market with a more disciplined and less emotional approach, potentially leading to better long-term outcomes.

## Getting Started

To get started with TradeWalls, follow these steps:

1. Clone the TradeWalls repository.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Start the autonomous agent by running `python trade_agent.py`. This bootstraps trading.sqlite so it must be run before app.py.
4. Start the server by running `python app.py`.
5. Set `MATTERMOST_WEBHOOK_URL` to a Mattermost incoming webhook for receiving time-sensitive buy/sell notifications. Our self-hosted server is https://chat.255labs.xyz; the webhook selects the destination channel. Keep its full URL in the runtime secret store, never git. See `notification.py`.
6. Restart `trade_agent.py` with `MATTERMOST_WEBHOOK_URL` defined

To ensure that your TradeWalls setup runs continuously and reliably for years, consider the following:

- Use a process manager like PM2 to keep the server and agent running in the background and automatically restart them if they crash.
- Set up monitoring and alerting systems to track the uptime and performance of your TradeWalls installation.
- Regularly review and update your trading walls to adapt to changing market conditions and your evolving investment strategy.
- Contact us at [255labs.xyz](https://255labs.xyz) if you need automated trading, additional features or other custom development.

Be sure to backup `trading.sqlite`

## When a trade wall bid is hit

1. TradeWalls will alert the MATTERMOST_WEBHOOK_URL that your trade is possible
2. It will assume the trade went through for the amount given (written to trading.sqlite)
2. You will have to make the trade.
3. It will be ready for the ask to hit

## Notification migration

This local-only tool has no catalogued running deployment. The optional notifier uses `MATTERMOST_WEBHOOK_URL`; the old generic `WEBHOOK_URL` variable is ignored. An unset or blank setting prints the notification to stdout. Requests use JSON, a five-second timeout, and best-effort delivery so a notification outage cannot interrupt trade handling. No message body or webhook secret is logged on failure.

If an operator has an uncatalogued instance, back up its process configuration privately, set the new webhook, restart with its normal process manager, and confirm a notification canary without placing a trade. Roll back code and configuration together to the prior revision if needed, before retiring the old credential. This PR does not deploy or re-enable a trading agent. Track cutover with the inventory Slack-to-Mattermost release blitz.

Validate locally with `python3 -m unittest discover -s tests -v` (local HTTP receiver only).
