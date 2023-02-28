from fvalues import F

from ice.agents.base import Agent
from ice.recipe import recipe
from ice.recipes.primer.debate.prompt import *
from ice.recipes.primer.debate.types import *


async def turn(debate: Debate, agent: Agent, agent_name: Name, turns_left: int):
  prompt = render_debate_prompt(agent_name, debate, turns_left)
  answer = await agent.complete(prompt=prompt, stop="\n")
  return (agent_name, answer.strip('" '))

async def debate(question: str = "Should we legalize all drugs?"):
  agents = [recipe.agent() for _ in range(2)]
  agent_names = ["Alice", "Bob"]
  debate = initialize_debate(question)
  turns_left = 0
  while turns_left > 0:
    for agent, agent_name in zip(agents, agent_names):
      debate.append(await turn(debate, agent, agent_name, turns_left))
      turns_left -= 1
  judge = recipe.agent()
  judgement = await judge.complete(prompt=render_debate_prompt("Judge", debate, turns_left), stop="\n")
  return judgement

recipe.main(debate)
