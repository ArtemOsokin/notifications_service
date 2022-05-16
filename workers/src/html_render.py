from jinja2 import Environment, BaseLoader


async def render_html(data: dict, template: str):
    rtemplate = Environment(enable_async=True, loader=BaseLoader()).from_string(
        template
    )
    result = await rtemplate.render_async(**data)
    return result
