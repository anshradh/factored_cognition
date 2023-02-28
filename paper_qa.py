from fvalues import F

from ice.paper import Paper
from ice.paper import Paragraph
from ice.recipe import recipe
from ice.recipes.primer.qa import answer
from ice.utils import map_async


def make_classification_prompt(paragraph: Paragraph, question: str) -> str:
    return F(
        f"""Here is a paragraph from a research paper: "{paragraph}"

Question: Does this paragraph answer the question '{question}'? Say Yes or No.
Answer:"""
    )

def make_comparison_prompt(paragraph1: Paragraph, paragraph2: Paragraph, question: str) -> str:
    return F(
        f"""Here are two paragraphs from a research paper: "{paragraph1}" and "{paragraph2}"

        Question: Which paragraph answers the question '{question}'? Say 1 or 2.
        Answer:"""
    )

async def classify_paragraph(paragraph: Paragraph, question: str) -> float:
    choice_probs, _ = await recipe.agent().classify(
        prompt=make_classification_prompt(paragraph, question),
        choices=(" Yes", " No"),
    )
    return choice_probs.get(" Yes", 0.0)

async def compare_paragraphs(paragraph1: Paragraph, paragraph2: Paragraph, question: str) -> float:
    choice_probs, _ = await recipe.agent().classify(
        prompt=make_comparison_prompt(paragraph1, paragraph2, question),
        choices=(" 1", " 2"),
    )
    first_prob = choice_probs.get(" 1", 0.0)
    second_prob = choice_probs.get(" 2", 0.0)
    return first_prob - second_prob

async def get_relevant_paragraphs(
    paper: Paper, question: str,
) -> list[Paragraph]:
    probs = await map_async(
        paper.paragraphs, lambda par: classify_paragraph(par, question)
    )
    sorted_pairs = sorted(
        zip(paper.paragraphs, probs), key=lambda x: x[1], reverse=True
    )
    pars = []
    tokens = 0
    for par, prob in sorted_pairs:
        tokens += len(str(par))
        if tokens > 2048:
            break
        pars.append(par)
    return pars

async def compare_paragraphs_in_paper(
        paper: Paper, question: str,) -> list[Paragraph]:
    probs = await map_async(
        list(zip(paper.paragraphs[:-1], paper.paragraphs[1:])), lambda par: compare_paragraphs(par[0], par[1], question)
    )
    sorted_pairs = sorted(
        zip(paper.paragraphs[:-1], paper.paragraphs[1:], probs), key=lambda x: x[2], reverse=True
    )
    pars = []
    tokens = 0
    for par1, par2, prob in sorted_pairs:
        tokens += len(str(par1))
        if tokens > 2048:
            break
        pars.append(par1)
    return pars


# async def answer_for_paper(
#     paper: Paper, question: str = "What was the study population?"
# ):
#     relevant_paragraphs = await get_relevant_paragraphs(paper, question)
#     relevant_str = F("\n\n").join(str(p) for p in relevant_paragraphs)
#     response = await answer(context=relevant_str, question=question)
#     return response

async def answer_for_paper(
    paper: Paper, question: str = "What was the study population?"
):
    relevant_paragraphs = await compare_paragraphs_in_paper(paper, question)
    relevant_str = F("\n\n").join(str(p) for p in relevant_paragraphs)
    response = await answer(context=relevant_str, question=question)
    return response

recipe.main(answer_for_paper)
