"""Tests de ui/views.py con fakes (sin gateway)."""

import unittest

from ui.views import EnqueueSelectView, PagerView


class FakeResponse:
    def __init__(self):
        self.sent = []
        self.edited = []

    async def send_message(self, content=None, **kwargs):
        self.sent.append(content)

    async def edit_message(self, **kwargs):
        self.edited.append(kwargs)


class FakeSelectInteraction:
    def __init__(self, user_id, values):
        self.user = type("U", (), {"id": user_id})()
        self.data = {"values": values}
        self.response = FakeResponse()


def run(coro):
    import asyncio

    return asyncio.run(coro)


class EnqueueSelectTest(unittest.TestCase):
    def test_opciones_y_pick(self):
        picked = []

        async def on_pick(inter, i, payload):
            picked.append((i, payload))

        async def scenario():
            view = EnqueueSelectView(
                options=[("A", "d1", "pa"), ("B", "d2", "pb")],
                requester_id=7,
                on_pick=on_pick,
            )
            await view._select_callback(FakeSelectInteraction(7, ["1"]))
            return view

        view = run(scenario())
        select = view.children[0]
        self.assertEqual([o.label for o in select.options], ["A", "B"])
        self.assertEqual(picked, [(1, "pb")])

    def test_tercero_rechazado(self):
        picked = []

        async def on_pick(inter, i, payload):
            picked.append(payload)

        async def scenario():
            view = EnqueueSelectView(options=[("A", "", "pa")], requester_id=7, on_pick=on_pick)
            inter = FakeSelectInteraction(9, ["0"])
            await view._select_callback(inter)
            return inter

        inter = run(scenario())
        self.assertEqual(picked, [])
        self.assertIn("Solo quien pidió", inter.response.sent[-1])

    def test_indice_invalido(self):
        async def on_pick(inter, i, payload):
            pass

        async def scenario():
            view = EnqueueSelectView(options=[("A", "", "pa")], requester_id=7, on_pick=on_pick)
            inter = FakeSelectInteraction(7, ["9"])
            await view._select_callback(inter)
            return inter

        inter = run(scenario())
        self.assertIn("inválida", inter.response.sent[-1].lower())

    def test_timeout_avisa(self):
        async def on_pick(inter, i, payload):
            pass

        class FakeOrig:
            def __init__(self):
                self.edited = []

            async def edit_original_response(self, **kwargs):
                self.edited.append(kwargs)

        async def scenario():
            orig = FakeOrig()
            view = EnqueueSelectView(
                options=[("A", "", "pa")],
                requester_id=7,
                on_pick=on_pick,
                on_timeout_edit=(orig, "expiró"),
            )
            await view.on_timeout()
            return orig

        orig = run(scenario())
        self.assertEqual(orig.edited[-1]["content"], "expiró")


class PagerTest(unittest.TestCase):
    def test_navegacion_y_clamp(self):
        async def scenario():
            view = PagerView(total_pages=3, render=lambda p: f"embed-{p}")
            states = [(view.prev_btn.disabled, view.next_btn.disabled)]
            await view.next_btn.callback(FakeSelectInteraction(1, []))
            await view.next_btn.callback(FakeSelectInteraction(1, []))
            await view.next_btn.callback(FakeSelectInteraction(1, []))
            states.append((view.page, view.next_btn.disabled))
            await view.prev_btn.callback(FakeSelectInteraction(1, []))
            states.append(view.page)
            return view, states

        view, states = run(scenario())
        self.assertEqual(states[0], (True, False))
        self.assertEqual(states[1], (3, True))
        self.assertEqual(states[2], 2)

    def test_una_pagina_todo_deshabilitado(self):
        async def scenario():
            return PagerView(total_pages=1, render=lambda p: "x")

        view = run(scenario())
        self.assertTrue(view.prev_btn.disabled)
        self.assertTrue(view.next_btn.disabled)


if __name__ == "__main__":
    unittest.main()
