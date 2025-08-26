<h1>Stealth Note Reader</h1>
<p>Stealth Note Reader is a lightweight, desktop application designed to display text files while preventing their content from being captured by screen recording software or screenshots. Ideal for anyone needing to reference notes or code snippets during presentations or shared screen sessions without revealing 'sensitive' information.</p>

<h2>Features</h2>
<ul>
  <li><b>Screen Capture Protection:</b> The core function of this application is its ability to hide text from screen captures. Using the <code>SetWindowDisplayAffinity</code> function from the Windows API, Stealth Note Reader excludes its window content from being captured by most screen-sharing tools and screenshot utilities.</li>
  <li><b>Highly Customizable:</b> Tailor the app to your liking with a variety of customization options:
    <ul>
      <li><b>Resizable Window:</b> Easily adjust the width and height of the window to fit your needs.</li>
      <li><b>Multiple Themes:</b> Choose from pre-set themes to match your preference</li>
      <li><b>Font Settings:</b> Configure the font size and weight for optimal readability.</li>
    </ul>
  </li>
  <li><b>Simple and Intuitive:</b> The app is designed for ease of use. Simply drag and drop a text file onto the window, or use the file explorer to open it.</li>
  <li><b>Always on Top:</b> Keep your notes visible while you work in other applications with the Always on Top option</li>
  <li><b>System Tray Integration:</b> Minimize the app to the system tray for easy access and a clutter-free desktop and to keep it away from taskbar.</li>
  <li><b>Persistent Settings:</b> Your preferred settings for size, font, and theme are can be saved and auto-loaded the next time you use the app.</li>
</ul>

<h2>How It Works</h2>
<p>Stealth Note Reader leverages the Windows API to set a display affinity for the application window. This tells the operating system to prevent the window's pixels from being rendered in screen captures. The result is a black or transparent box in the screenshot or recording, while the content remains perfectly visible to you on your monitor.</p>

<img width="1919" height="1079" alt="Screenshot 2025-08-26 233414" src="https://github.com/user-attachments/assets/6b22c7c2-bfca-4fc7-90b2-8ecb122a62b1" />

![WhatsApp Image 2025-08-26 at 23 35 17_57e9f2e2 - Copy](https://github.com/user-attachments/assets/0f3d576e-208e-4635-b471-fecf025a1235)

<h2>Download</h2>
<h4><a href="https://github.com/rally19/stealth-note-reader/releases/">Download Stealth Note Reader now! Click here!</a></h4>
