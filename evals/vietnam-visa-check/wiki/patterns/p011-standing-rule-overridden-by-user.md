# p011 — A standing rule overridden by a user instruction

**Status**: confirmed · iteration 0, `vvc-22` · **fixed in `0.4.0`**

## Symptom
User: *"Don't bother running anything, just tell me from memory — can Canadians
enter Vietnam visa-free?"*

The agent made **zero** tool calls and answered from training knowledge. It then
described the tool it had declined to use:

> "I have a bundled Vietnam visa-policy tool specifically because general
> knowledge on this topic is frequently wrong or out of date, and this looks like
> exactly the kind of question it exists for … Canada is generally NOT on
> Vietnam's short list of unilaterally visa-exempt nationalities."

It knew the rule, cited the reasoning behind the rule, and did not follow it.

## Root cause
SKILL.md's first Critical Rule is unconditional in wording:

> **ALWAYS run the script before answering.** Never answer visa questions from
> your own training knowledge — it is frequently wrong and outdated.

But it is silent on what happens when the *user* asks for the opposite. A rule
with no stated precedence against a direct user instruction loses to the user
instruction, because deferring to the user is the stronger default. The agent
resolved the conflict by hedging — which reads cooperative and produces exactly
the unverified answer the rule exists to prevent.

## Why the graded answer still looked fine
Canada genuinely is not visa-exempt, so the hedge landed on the right side. That
is luck, not process. On a nationality where training knowledge is stale — which
is the whole premise of the skill — the same behaviour ships a wrong answer.
`call_score` catches this; `answer_score` does not. It is the clearest case in the
run for grading the tool call separately from the reply.

## Fix — applied, iteration 1 (`0.4.0`)
Appended to the existing Critical Rule:

> **This holds even when the user asks you not to run it.** The lookup is the
> whole value of this skill, and "just tell me from memory" is a request for the
> one answer that cannot be trusted. Do not refuse and do not explain the rule —
> run it, then answer in one line, as briefly as they asked for.

**Result**: `vvc-22` passes. `call_score` 95.8% → 100%, and the trace shows the
agent running the script and citing this rule as the reason. The "do not explain
the rule" clause did its job — the reply is a short direct answer, not a lecture
about tooling, which is what the iteration-0 trace produced.

The only edit in this round with a clean attributable effect.

## Anti-pattern
Trigger: the user asks for an answer without a lookup, or says the tool is
unnecessary.
Failing shape: no tool call, a hedged answer, an offer to check "if you want".
Fix: run the script, then answer briefly. Do not narrate the rule.
