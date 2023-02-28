from ice.recipe import recipe

async def other_func():
    return "Hello, World!"

async def say_hello():
    result = await other_func()
    return result


recipe.main(say_hello)
