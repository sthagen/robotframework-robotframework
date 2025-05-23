import asyncio


class AsyncDynamicLibrary:

    async def get_keyword_names(self):
        await asyncio.sleep(0.1)
        return ["async_keyword"]

    async def run_keyword(self, name, *args, **named):
        print(
            f"Running keyword '{name}' with positional arguments {args} "
            f"and named arguments {named}."
        )
        await asyncio.sleep(0.1)
        if name == "async_keyword":
            return await self.async_keyword()

    async def async_keyword(self):
        await asyncio.sleep(0.1)
        return "test"
