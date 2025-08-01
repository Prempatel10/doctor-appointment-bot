#!/usr/bin/env python3

import json
import os
from typing import Dict, Any


class MultiLanguageSupport:
    """Multi-language support for the bot."""
    
    def __init__(self):
        self.translations = {
            'en': {
                'welcome_message': """
🏥 **Welcome to Doctor Appointment Bot, {}!**

I'll help you book an appointment with our doctors.

Available Services:
• Book new appointment
• View available doctors
• Quick and easy scheduling

Click /book to start booking an appointment!
Or use the menu below:
""",
                'book_appointment': '📅 Book Appointment',
                'view_doctors': '👨‍⚕️ View Doctors',
                'help': '❓ Help',
                'contact': '📞 Contact',
                'select_doctor': '👨‍⚕️ **Please select a doctor:**',
                'enter_name': '👤 **Please enter your full name:**',
                'select_age': '👤 **Please select your age group:**',
                'select_gender': '⚧ **Please select your gender:**',
                'enter_phone': '📞 **Please enter your phone number:**',
                'enter_email': '📧 **Please enter your email address:**',
                'chief_complaint': '🏥 **Please describe your chief complaint or reason for visit:**',
                'select_date': '📅 **Please select your preferred date:**',
                'select_time': '🕐 **Please select your preferred time:**',
                'additional_notes': '❓ **Additional Notes (Optional)**',
                'confirm_appointment': '✅ Confirm Appointment',
                'appointment_confirmed': '🎉 **Appointment Confirmed Successfully!**',
                'back': '🔙 Back',
                'cancel': '❌ Cancel',
                'male': '👨 Male',
                'female': '👩 Female',
                'other': '🏳️‍⚧️ Other',
                'none': 'None'
            },
            'es': {
                'welcome_message': """
🏥 **¡Bienvenido al Bot de Citas Médicas, {}!**

Te ayudaré a reservar una cita con nuestros médicos.

Servicios Disponibles:
• Reservar nueva cita
• Ver médicos disponibles
• Programación rápida y fácil

¡Haz clic en /book para comenzar a reservar una cita!
O usa el menú de abajo:
""",
                'book_appointment': '📅 Reservar Cita',
                'view_doctors': '👨‍⚕️ Ver Médicos',
                'help': '❓ Ayuda',
                'contact': '📞 Contacto',
                'select_doctor': '👨‍⚕️ **Por favor selecciona un médico:**',
                'enter_name': '👤 **Por favor ingresa tu nombre completo:**',
                'select_age': '👤 **Por favor selecciona tu grupo de edad:**',
                'select_gender': '⚧ **Por favor selecciona tu género:**',
                'enter_phone': '📞 **Por favor ingresa tu número de teléfono:**',
                'enter_email': '📧 **Por favor ingresa tu dirección de email:**',
                'chief_complaint': '🏥 **Por favor describe tu queja principal o razón de la visita:**',
                'select_date': '📅 **Por favor selecciona tu fecha preferida:**',
                'select_time': '🕐 **Por favor selecciona tu hora preferida:**',
                'additional_notes': '❓ **Notas Adicionales (Opcional)**',
                'confirm_appointment': '✅ Confirmar Cita',
                'appointment_confirmed': '🎉 **¡Cita Confirmada Exitosamente!**',
                'back': '🔙 Atrás',
                'cancel': '❌ Cancelar',
                'male': '👨 Masculino',
                'female': '👩 Femenino',
                'other': '🏳️‍⚧️ Otro',
                'none': 'Ninguno'
            },
            'fr': {
                'welcome_message': """
🏥 **Bienvenue au Bot de Rendez-vous Médical, {}!**

Je vous aiderai à prendre rendez-vous avec nos médecins.

Services Disponibles:
• Prendre un nouveau rendez-vous
• Voir les médecins disponibles
• Planification rapide et facile

Cliquez sur /book pour commencer à prendre rendez-vous!
Ou utilisez le menu ci-dessous:
""",
                'book_appointment': '📅 Prendre Rendez-vous',
                'view_doctors': '👨‍⚕️ Voir Médecins',
                'help': '❓ Aide',
                'contact': '📞 Contact',
                'select_doctor': '👨‍⚕️ **Veuillez sélectionner un médecin:**',
                'enter_name': '👤 **Veuillez entrer votre nom complet:**',
                'select_age': '👤 **Veuillez sélectionner votre groupe d\'âge:**',
                'select_gender': '⚧ **Veuillez sélectionner votre genre:**',
                'enter_phone': '📞 **Veuillez entrer votre numéro de téléphone:**',
                'enter_email': '📧 **Veuillez entrer votre adresse email:**',
                'chief_complaint': '🏥 **Veuillez décrire votre plainte principale ou raison de la visite:**',
                'select_date': '📅 **Veuillez sélectionner votre date préférée:**',
                'select_time': '🕐 **Veuillez sélectionner votre heure préférée:**',
                'additional_notes': '❓ **Notes Supplémentaires (Optionnel)**',
                'confirm_appointment': '✅ Confirmer Rendez-vous',
                'appointment_confirmed': '🎉 **Rendez-vous Confirmé avec Succès!**',
                'back': '🔙 Retour',
                'cancel': '❌ Annuler',
                'male': '👨 Masculin',
                'female': '👩 Féminin',
                'other': '🏳️‍⚧️ Autre',
                'none': 'Aucun'
            },
            'hi': {
                'welcome_message': """
🏥 **डॉक्टर अपॉइंटमेंट बॉट में आपका स्वागत है, {}!**

मैं आपको हमारे डॉक्टरों के साथ अपॉइंटमेंट बुक करने में मदद करूंगा।

उपलब्ध सेवाएं:
• नई अपॉइंटमेंट बुक करें
• उपलब्ध डॉक्टर देखें
• त्वरित और आसान शेड्यूलिंग

अपॉइंटमेंट बुक करना शुरू करने के लिए /book पर क्लिक करें!
या नीचे दिए गए मेनू का उपयोग करें:
""",
                'book_appointment': '📅 अपॉइंटमेंट बुक करें',
                'view_doctors': '👨‍⚕️ डॉक्टर देखें',
                'help': '❓ सहायता',
                'contact': '📞 संपर्क',
                'select_doctor': '👨‍⚕️ **कृपया एक डॉक्टर चुनें:**',
                'enter_name': '👤 **कृपया अपना पूरा नाम दर्ज करें:**',
                'select_age': '👤 **कृपया अपना आयु समूह चुनें:**',
                'select_gender': '⚧ **कृपया अपना लिंग चुनें:**',
                'enter_phone': '📞 **कृपया अपना फ़ोन नंबर दर्ज करें:**',
                'enter_email': '📧 **कृपया अपना ईमेल पता दर्ज करें:**',
                'chief_complaint': '🏥 **कृपया अपनी मुख्य शिकायत या यात्रा का कारण बताएं:**',
                'select_date': '📅 **कृपया अपनी पसंदीदा तारीख चुनें:**',
                'select_time': '🕐 **कृपया अपना पसंदीदा समय चुनें:**',
                'additional_notes': '❓ **अतिरिक्त नोट्स (वैकल्पिक)**',
                'confirm_appointment': '✅ अपॉइंटमेंट कन्फर्म करें',
                'appointment_confirmed': '🎉 **अपॉइंटमेंट सफलतापूर्वक कन्फर्म हुई!**',
                'back': '🔙 वापस',
                'cancel': '❌ रद्द करें',
                'male': '👨 पुरुष',
                'female': '👩 महिला',
                'other': '🏳️‍⚧️ अन्य',
                'none': 'कोई नहीं'
            }
        }
        
        self.supported_languages = ['en', 'es', 'fr', 'hi']
        self.default_language = 'en'
    
    def get_text(self, key: str, language: str = 'en', *format_args, **format_kwargs) -> str:
        """Get translated text for a given key and language."""
        if language not in self.supported_languages:
            language = self.default_language
        
        text = self.translations.get(language, {}).get(key, 
               self.translations[self.default_language].get(key, f"Missing translation: {key}"))
        
        # Handle both positional and keyword arguments for formatting
        if format_args or format_kwargs:
            try:
                if format_args:
                    return text.format(*format_args, **format_kwargs)
                else:
                    return text.format(**format_kwargs)
            except (KeyError, IndexError, ValueError) as e:
                # If formatting fails, return the unformatted text
                return text
        return text
    
    def get_language_menu(self) -> list:
        """Get language selection menu."""
        return [
            ['🇺🇸 English', '🇪🇸 Español'],
            ['🇫🇷 Français', '🇮🇳 हिंदी']
        ]
    
    def detect_language_from_text(self, text: str) -> str:
        """Simple language detection based on text patterns."""
        # This is a basic implementation - you might want to use a proper language detection library
        if any(char in text for char in ['ñ', 'á', 'é', 'í', 'ó', 'ú']):
            return 'es'
        elif any(char in text for char in ['à', 'é', 'è', 'ê', 'ç', 'ù']):
            return 'fr'
        elif any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in text):
            return 'hi'
        else:
            return 'en'
    
    def save_user_language(self, user_id: int, language: str):
        """Save user's preferred language to a file."""
        try:
            user_languages = {}
            if os.path.exists('user_languages.json'):
                with open('user_languages.json', 'r', encoding='utf-8') as f:
                    user_languages = json.load(f)
            
            user_languages[str(user_id)] = language
            
            with open('user_languages.json', 'w', encoding='utf-8') as f:
                json.dump(user_languages, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving user language: {e}")
            return False
    
    def get_user_language(self, user_id: int) -> str:
        """Get user's preferred language."""
        try:
            if os.path.exists('user_languages.json'):
                with open('user_languages.json', 'r', encoding='utf-8') as f:
                    user_languages = json.load(f)
                    return user_languages.get(str(user_id), self.default_language)
        except Exception as e:
            print(f"Error getting user language: {e}")
        return self.default_language
    
    def set_user_language_from_selection(self, selection: str) -> str:
        """Convert language selection to language code."""
        language_map = {
            '🇺🇸 English': 'en',
            '🇪🇸 Español': 'es', 
            '🇫🇷 Français': 'fr',
            '🇮🇳 हिंदी': 'hi'
        }
        return language_map.get(selection, 'en')


if __name__ == "__main__":
    # Example Usage:
    ml = MultiLanguageSupport()
    
    # Test translations
    print("English:", ml.get_text('welcome_message', 'en', 'John'))
    print("Spanish:", ml.get_text('welcome_message', 'es', 'Juan'))
    print("French:", ml.get_text('welcome_message', 'fr', 'Jean'))
    print("Hindi:", ml.get_text('welcome_message', 'hi', 'राम'))
