class Step:
    def __init__(self, name, func, retries=1):
        self.name = name
        self.func = func
        self.retries = retries

class Workflow:
    def __init__(self, name):
        self.name = name
        self.steps = []

    def add(self, step):
        self.steps.append(step)
        return self

    def run(self, ctx):
        for step in self.steps:
            for attempt in range(1, step.retries + 1):
                try:
                    print(f'[{self.name}] {step.name} attempt {attempt}')
                    result = step.func(ctx)
                    if result is False:
                        raise RuntimeError(f'{step.name} returned False')
                    ctx[step.name] = result
                    break
                except Exception as e:
                    print(f'[warn] {step.name}: {e}')
                    if attempt == step.retries:
                        raise
        return ctx

def fetch_prompt(ctx):
    ctx['prompt'] = ctx.get('raw', '').strip()
    return ctx['prompt']

def maybe_translate(ctx):
    if ctx.get('lang') == 'en':
        ctx['prompt'] = 'Translate to Chinese: ' + ctx['prompt']
    return ctx['prompt']

def fake_llm(ctx):
    prompt = ctx['prompt']
    if not prompt:
        raise ValueError('empty prompt')
    return f'LLM answer for: {prompt[:30]}'

def postprocess(ctx):
    return ctx['fake_llm'].replace('answer', 'response')

if __name__ == '__main__':
    wf = Workflow('demo')
    wf.add(Step('fetch_prompt', fetch_prompt))
    wf.add(Step('maybe_translate', maybe_translate))
    wf.add(Step('fake_llm', fake_llm, retries=2))
    wf.add(Step('postprocess', postprocess))
    out = wf.run({'raw': '  Build a workflow demo  ', 'lang': 'en'})
    print(out['postprocess'])