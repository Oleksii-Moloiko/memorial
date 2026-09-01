from .constants import MEMORY_TEASER_LIMIT


def make_memory_teaser(text):
    if len(text) <= MEMORY_TEASER_LIMIT:
        return text

    cut = text[:MEMORY_TEASER_LIMIT]
    last_space = cut.rfind(" ")

    if last_space > 0:
        return cut[:last_space].rstrip()

    return cut.rstrip()