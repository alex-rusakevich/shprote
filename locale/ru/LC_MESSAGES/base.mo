��    :      �  O   �      �  ,   �  	  &  .   0  F  _  I   �     �     	     &	    @	     ^
     {
     �
  !   �
  @   �
          *  &   :     a     v  D   �     �      �       [   .  (   �  .   �      �  �     �   �  7   3     k  +   �  	   �     �  .   �  5   �  6   .  6   e     �  �   �  �   ;     �     �     �  	             )     >     G  7   a     �  *   �  E   �  a     *   z  %   �     �  �   �  F   �  �    <   �    �  �   �  %   �  &   �  9   �    4  1   M  7     ;   �  4   �  l   (  2   �     �  ;   �  1     1   P  z   �  (   �  _   &   4   �   �   �   D   R!  w   �!  i   "  e  y"  g  �#  _   G%  ;   �%  ?   �%     #&     :&  d   S&  \   �&  [   '  _   q'     �'  2  �'  �  )     �*      �*  /   �*     '+  .   5+  ,   d+     �+  ;   �+  q   �+     M,  ;   e,  �   �,  �   6-  i   �-  L   Z.     �.                  0               8   .      4   2      9          1      #      ,      
   	   !   (                     /       *         :                                +   -           &   )            6                 "       7       %                5      $      3             '    

<b>Student → teacher:</b>
{telebot_diff} 
*All users:* {users_in_total} ({new_users_month} this month, {new_users_year} this year)
*Active users this year:* {active_users_this_year} ({new_active_users_this_year})
*Active users this month:* {active_users_this_month} ({new_active_users_this_month})
         
*Something went wrong*
{err_name}: {err_msg}
 
*Standardized 汉语 Pronunciation TEster {__version__}*
Created by Alexander Rusakevich (https://github.com/alex-rusakevich)

/start — start the bot and go to the main menu
/help — display this message
/checkpr — begin your pronunciation check. The special code / hash in bot replies is intended to avoid pupil cheating by sending different results or fake tasks
/checklisten — begin the listening check
/stop — stop the check and go to main menu

_May 汉语 be with you!_

_Special thanks to the authors of {used_packages_exc_last} and {used_packages_last} libraries_
 *The answer cannot be forwarded or be a reply. The test has been failed.* *[DONE BY THE STUDENT]* *[FORWARDED FROM {usr_name}]* *[REPLIED TO {usr_name}]* <b>Your {test_type} check result is {perc}% ({phon_mistakes} phonematic mistake(s))</b>
<i>Now you can forward all the messages with the special code to your teacher</i>{student_to_teacher}

<b>Teacher's transcription:</b> {teacher_repr}

<b>Student's transcription:</b> {student_repr} Checking your telegram id... Choose your language, please: Done, no more logs left to send Getting back to the admin menu... Hello there, {name}! I'm ready to check your pronunciation! 🤓 Hello, admin! Here you are... I do hope you know what you've done... Now wait a little... Returning to the main menu Student said: {student}
*The signed voice message will appear below* Student wrote: {student} Student's signed voice message,  Switching back to the menu... Teacher said {forwarded_msg}: {teacher}
*The signed voice message itself will appear below* Teacher wrote {forwarded_msg}: {teacher} Teacher's signed voice message {forwarded_msg} Teacher's signed voice message,  The *listening* check has started. _Please, remember that you cannot use replied or forwarded messages as student's answers._ Check's special code is The *pronunciation* check has started. _Please, remember that you cannot use replied or forwarded messages as student's answers._ Check's special code is The check has been stopped. Getting back to the menu... Welcome to the main menu! Write to ⚠ *all* ⚠ the registred users: listening pronunciation ⏳ Processing the audio file, please, wait... ⛔ The password is wrong, returning to the main menu ⛔ Your id is not allowed, returning to the main menu ✅ The id is correct. Now enter the password, please: ❌ Stop ❓ Enter or redirect teacher's audio file or voice message or reply to it _(redirect and reply have the highest priority of the messages you send)_: ❓ Enter or redirect teacher's text or voice message or reply to it _(redirect and reply have the highest priority of the messages you send)_: ❓ Help ❓ Student's answer: ❓ Student's voice record: 🍱 Menu 🎤 Check pronunciation 👂 Check listening 📜 Log 📣 Message to all users 🔴 Cannot process this file, please, try another one: 🔴 Shutdown 🔴 There is no such language: {langname} 🔴 Wrong data type ("{data_type}"), please, send a _voice_ message: 🔴 Wrong data type ("{data_type}"), please, send a voice message or an audio (.mp3, .ogg) file: 🔴 Wrong data type, please, send _text_: 🟢 Done! {msg_count} messages sent! 🧮 Statistics Project-Id-Version: 
Report-Msgid-Bugs-To: 
PO-Revision-Date: 2024-11-03 23:10+0300
Last-Translator: 
Language-Team: 
Language: ru
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
X-Generator: Poedit 3.4.2
 

<b>Студент → преподаватель:</b>
{telebot_diff} 
*Все пользователи:* {users_in_total} ({new_users_month} в этом месяце, {new_users_year} в этом году)
*Активных пользователей в этом году:* {active_users_this_year} ({new_active_users_this_year})
*Активных пользователей в этом месяце:* {active_users_this_month} ({new_active_users_this_month})
         
*Что-то пошло не так*
{err_name}: {err_msg}
 
*Программа проверки китайского произношения "shprote" {__version__}*
Создано Александром Русакевичем (https://github.com/alex-rusakevich)

/start — запустить бота и перейти в главное меню
/help — показать справку, которую вы сейчас читаете
/checkpr — начать проверку произношения. Специальный код / хэш в ответах бота используется для того, чтобы студент не смог послать разные ответы и результаты
/checklisten — начать проверку аудирования
/stop — остановить проверку и перейти в главное меню

_Да прибудет с вами китайский!_

_Особая благодарность выражается авторам библиотек {used_packages_exc_last} и {used_packages_last}_
 *В качестве ответа не могут быть использованы пересланные или отвеченные сообщения. Тест был провален* *[СДЕЛАНО СТУДЕНТОМ]* *[ПЕРЕСЛАНО ОТ {usr_name}]* *[ОТВЕТ ДЛЯ ПОЛЬЗОВАТЕЛЯ {usr_name}]* <b>Ваш результат проверки на {test_type}: {perc}% (кол-во фонематических ошибок: {phon_mistakes})</b>
<i>Теперь вы можете переслать все сообщения, помеченные специальным кодом, вашему преподавателю</i>{student_to_teacher}

<b>Транскрипция сказанного преподавателем:</b> {teacher_repr}

<b>Транскрипция сказанного студентом:</b> {student_repr} Проверяю ваш id в Телеграм... Пожалуйста, выберите ваш язык: Готово, все логи были отправлены Возвращаюсь в главное меню... Добрый день, {name}! Я готов к проверке вашего произношения! 🤓 Добрый день, администратор! Вот, держите... Надеюсь, вы знаете, что делаете... Теперь немного подождите... Возвращаюсь в главное меню Студент сказал: {student}
*Сообщение с цифровой подписью появится ниже* Студент написал: {student} Голосовое сообщение студента со специальным кодом,  Возвращаюсь в главное меню... Преподаватель сказал {forwarded_msg}: {teacher}
*Сообщение с цифровой подписью появится ниже* Преподаватель написал {forwarded_msg}: {teacher} Голосовое сообщение преподавателя со специальным кодом {forwarded_msg} Голосовое сообщение преподавателя со специальным кодом,  Проверка *аудирования* началась. _Пожалуйста, помните, что вы не можете использовать в качестве пересланные сообщения либо ответы на те сообщения, что выводились раньше._ Специальный код проверки Проверка *произношения* началась. _Пожалуйста, помните, что вы не можете использовать в качестве пересланные сообщения либо ответы на те сообщения, что выводились раньше._ Специальный код проверки Проверка остановлена. Возвращаемся в главное меню... Добро пожаловать в главное меню! Написать ⚠ *всем* ⚠ пользователям: аудирование произношение ⏳ Файл с аудио обрабатывается, пожалуйста, подождите... ⛔ Неправильный пароль, возвращаюсь в главное меню ⛔ Ваш id не был допущен, возвращаюсь в главное меню ✅ id подтвержден. Теперь, пожалуйста, введите пароль: ❌ Остановить ❓ Введите или перешлите от учителя аудиозапись или ответьте на сообщение с ним _(содержание отвеченных сообщений имеет приоритет выше, чем текст, которым вы ответили)_ ❓ Введите или перешлите текст или голосовое сообщение преподавателя или ответьте на него, если оно выводилось ранее _(если в ответе на сообщение будет текст, то принято будет только содержание пересланного/отвеченного сообщения)_: ❓ Помощь ❓ Ответ студента: ❓ Запись голоса студента: 🍱 Меню 🎤 Проверка произношения 👂 Проверка аудирования 📜 Логи 📣 Сообщение всем пользователям 🔴 Файл невозможно обработать, пожалуйста, попробуйте другой: 🔴 Выключить 🔴 Язык не поддерживается: {langname} 🔴 Неправильный тип данных ("{data_type}"), пожалуйста, отправьте _голосовое сообщение_: 🔴 Неправильный тип данных ("{data_type}"), пожалуйста, пошлите голосовое сообщение или файл с аудио (.mp3, .ogg): 🔴 Неправильный тип данных, пожалуйста, отправьте _текст_: 🟢 Готово! Отправлено {msg_count} сообщения(-е)! 🧮 Статистика 