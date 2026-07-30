import unittest

from src.services.intents import classify, get_prompt, INTENTS, STANDARD_PROMPT, CLARIFICATION_PROMPT


class IntentClassifierTests(unittest.TestCase):
    def test_clarification_triggers_detected(self):
        triggers = ["não entendi", "o que significa", "me explique", "pode explicar", "como assim"]
        for trigger in triggers:
            with self.subTest(trigger=trigger):
                self.assertEqual(classify(trigger), "clarification")

    def test_standard_messages_not_misclassified(self):
        messages = ["Hello! I want to practice", "How are you?", "I went to the store"]
        for msg in messages:
            with self.subTest(msg=msg):
                self.assertEqual(classify(msg), "standard")

    def test_case_insensitive(self):
        self.assertEqual(classify("NÃO ENTENDI"), "clarification")

    def test_fallback_to_standard(self):
        self.assertEqual(classify(""), "standard")


class StandardPromptTests(unittest.TestCase):
    def test_has_all_sections(self):
        self.assertIn("💬 CONVERSA", STANDARD_PROMPT)
        self.assertIn("📚 EXPLICAÇÃO", STANDARD_PROMPT)
        self.assertIn("📝 TEXTO CORRIGIDO", STANDARD_PROMPT)

    def test_conversation_in_english(self):
        self.assertIn("Always in English", STANDARD_PROMPT)

    def test_explanation_in_portuguese(self):
        self.assertIn("Always in Portuguese", STANDARD_PROMPT)

    def test_perfeito_when_no_errors(self):
        self.assertIn("Perfeito!", STANDARD_PROMPT)

    def test_do_not_invent_errors(self):
        self.assertIn("Do NOT invent errors", STANDARD_PROMPT)


class ClarificationPromptTests(unittest.TestCase):
    def test_has_translation_section(self):
        self.assertIn("💬 CONVERSA", CLARIFICATION_PROMPT)

    def test_has_explanation_section(self):
        self.assertIn("📚 EXPLICAÇÃO", CLARIFICATION_PROMPT)

    def test_translates_previous_response(self):
        self.assertIn("Translate your previous response", CLARIFICATION_PROMPT)

    def test_explains_difficult_words(self):
        self.assertIn("difficult English words", CLARIFICATION_PROMPT)

    def test_explains_grammar(self):
        self.assertIn("grammar structures", CLARIFICATION_PROMPT)

    def test_nada_de_difficil(self):
        self.assertIn("Nada de difícil!", CLARIFICATION_PROMPT)

    def test_no_corrected_text(self):
        self.assertNotIn("📝 TEXTO CORRIGIDO:", CLARIFICATION_PROMPT)

    def test_not_empty(self):
        self.assertTrue(len(CLARIFICATION_PROMPT) > 0)


class IntentSystemTests(unittest.TestCase):
    def test_get_prompt_returns_correct_prompt(self):
        self.assertEqual(get_prompt("standard"), STANDARD_PROMPT)
        self.assertEqual(get_prompt("clarification"), CLARIFICATION_PROMPT)

    def test_all_intents_have_prompt_key(self):
        for intent_name, config in INTENTS.items():
            with self.subTest(intent=intent_name):
                self.assertIn("prompt", config)
                self.assertIsInstance(config["prompt"], str)
                self.assertTrue(len(config["prompt"]) > 0)


if __name__ == "__main__":
    unittest.main()
