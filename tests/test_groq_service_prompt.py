import unittest

from src.services.intents import classify, get_prompt, INTENTS, STANDARD_PROMPT, CLARIFICATION_PROMPT


class IntentClassifierTests(unittest.TestCase):
    """Testes para o classificador de intenções."""

    def test_clarification_triggers_detected(self):
        triggers = ["não entendi", "o que significa", "me explique", "pode explicar", "como assim"]
        for trigger in triggers:
            with self.subTest(trigger=trigger):
                self.assertEqual(classify(trigger), "clarification")

    def test_standard_messages_not_misclassified(self):
        messages = [
            "Hello! I want to practice",
            "How are you today?",
            "Can you help me with grammar?",
            "I went to the store yesterday",
        ]
        for msg in messages:
            with self.subTest(msg=msg):
                self.assertEqual(classify(msg), "standard")

    def test_case_insensitive(self):
        self.assertEqual(classify("NÃO ENTENDI"), "clarification")
        self.assertEqual(classify("O Que Significa"), "clarification")

    def test_fallback_to_standard(self):
        self.assertEqual(classify(""), "standard")
        self.assertEqual(classify("anything else"), "standard")


class PromptTests(unittest.TestCase):
    """Testes para os prompts das intents."""

    def test_standard_prompt_has_sections(self):
        self.assertIn("💬 CONVERSA", STANDARD_PROMPT)
        self.assertIn("📚 EXPLICAÇÃO", STANDARD_PROMPT)
        self.assertIn("📝 TEXTO CORRIGIDO", STANDARD_PROMPT)

    def test_standard_prompt_requires_portuguese_explanation(self):
        self.assertIn("fully in Portuguese", STANDARD_PROMPT)

    def test_standard_prompt_minimal_corrections(self):
        self.assertIn("minimal change", STANDARD_PROMPT)
        self.assertIn("preserve the user's original meaning", STANDARD_PROMPT)

    def test_standard_prompt_forbids_extra_sections(self):
        self.assertIn("Only three top-level sections", STANDARD_PROMPT)

    def test_clarification_prompt_shows_english_first(self):
        self.assertIn("MENSAGEM EM INGLÊS", CLARIFICATION_PROMPT)
        self.assertIn("repita a frase em inglês", CLARIFICATION_PROMPT)

    def test_clarification_prompt_explains_in_portuguese(self):
        self.assertIn("EXPLICAÇÃO EM PORTUGUÊS", CLARIFICATION_PROMPT)
        self.assertIn("português", CLARIFICATION_PROMPT)

    def test_clarification_prompt_no_exercises(self):
        self.assertIn("Não adicione exercícios", CLARIFICATION_PROMPT)

    def test_get_prompt_returns_correct_prompt(self):
        self.assertEqual(get_prompt("standard"), STANDARD_PROMPT)
        self.assertEqual(get_prompt("clarification"), CLARIFICATION_PROMPT)

    def test_all_intents_have_prompts(self):
        for intent_name, config in INTENTS.items():
            with self.subTest(intent=intent_name):
                self.assertIn("prompt", config)
                self.assertIsInstance(config["prompt"], str)
                self.assertTrue(len(config["prompt"]) > 0)


if __name__ == "__main__":
    unittest.main()
