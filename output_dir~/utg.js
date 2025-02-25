var utg = 
{
  "nodes": [
    {
      "id": "e838b1325db49254e54c0709041c472a",
      "shape": "image",
      "image": "states/screen_2025-01-25_154248.jpg",
      "label": "QuickstepLauncher\n<FIRST>",
      "package": "com.transsion.XOSLauncher",
      "activity": "com.android.quickstep.src.com.android.launcher3.uioverrides.QuickstepLauncher",
      "state_str": "e838b1325db49254e54c0709041c472a",
      "structure_str": "c3a178761d1112062734ed8b64b82a62",
      "title": "<table class=\"table\">\n<tr><th>package</th><td>com.transsion.XOSLauncher</td></tr>\n<tr><th>activity</th><td>com.android.quickstep.src.com.android.launcher3.uioverrides.QuickstepLauncher</td></tr>\n<tr><th>state_str</th><td>e838b1325db49254e54c0709041c472a</td></tr>\n<tr><th>structure_str</th><td>c3a178761d1112062734ed8b64b82a62</td></tr>\n</table>",
      "content": "com.transsion.XOSLauncher\ncom.android.quickstep.src.com.android.launcher3.uioverrides.QuickstepLauncher\ne838b1325db49254e54c0709041c472a\nandroid:id/content,com.transsion.XOSLauncher:id/workspace,com.transsion.XOSLauncher:id/page_indicator,com.transsion.XOSLauncher:id/launcher,com.transsion.XOSLauncher:id/hotseat,com.transsion.XOSLauncher:id/layout,com.transsion.XOSLauncher:id/preview_background,com.transsion.XOSLauncher:id/drag_layer,com.transsion.XOSLauncher:id/apps_view_container,com.transsion.XOSLauncher:id/folder_icon_name\n\u25cf Easy Voice Recorder,DroidBot,Chatter,\u25cf Sportzfy,\u25cf X,\u25cf Palm Store,My App,\u25cf Instagram,\u25cf 1.1.1.1,\u25cf Messenger,\u25cf Clash of Clans,Football Live HD,FileDropper,\u25cf Pathao,Expenser,\u25cf Docs,Nagad,\u25cf Facebook,\u25cf PLAYit,Freezer,Camo Camera,\u25cf Telegram,Cleaner,\u25cf Ridmik,\u25cf Lite,\u25cf WhatsApp,\u25cf Water Sort Puzzle,\u25cf Gemini,\u25cf Foodi,Authenticator,GitStat",
      "font": "14px Arial red"
    },
    {
      "id": "b49ae4a12aec1025e366bba30c1075bf",
      "shape": "image",
      "image": "states/screen_2025-01-25_154251.jpg",
      "label": "Splash\n<LAST>",
      "package": "com.example.chatter",
      "activity": ".Splash",
      "state_str": "b49ae4a12aec1025e366bba30c1075bf",
      "structure_str": "9f68fabee18d7d88dc8d0bc3ed3b6f7e",
      "title": "<table class=\"table\">\n<tr><th>package</th><td>com.example.chatter</td></tr>\n<tr><th>activity</th><td>.Splash</td></tr>\n<tr><th>state_str</th><td>b49ae4a12aec1025e366bba30c1075bf</td></tr>\n<tr><th>structure_str</th><td>9f68fabee18d7d88dc8d0bc3ed3b6f7e</td></tr>\n</table>",
      "content": "com.example.chatter\n.Splash\nb49ae4a12aec1025e366bba30c1075bf\ncom.example.chatter:id/appName,android:id/content,com.example.chatter:id/action_bar_root,android:id/navigationBarBackground,com.example.chatter:id/developer,android:id/statusBarBackground,com.example.chatter:id/logoImg\n\u00a9 Saimon,Chatter",
      "font": "14px Arial red"
    }
  ],
  "edges": [
    {
      "from": "e838b1325db49254e54c0709041c472a",
      "to": "b49ae4a12aec1025e366bba30c1075bf",
      "id": "e838b1325db49254e54c0709041c472a-->b49ae4a12aec1025e366bba30c1075bf",
      "title": "<table class=\"table\">\n<tr><th>3</th><td>IntentEvent(intent='am start com.example.chatter/com.example.chatter.Splash')</td></tr>\n</table>",
      "label": "3",
      "events": [
        {
          "event_str": "IntentEvent(intent='am start com.example.chatter/com.example.chatter.Splash')",
          "event_id": 3,
          "event_type": "intent",
          "view_images": []
        }
      ]
    },
    {
      "from": "b49ae4a12aec1025e366bba30c1075bf",
      "to": "e838b1325db49254e54c0709041c472a",
      "id": "b49ae4a12aec1025e366bba30c1075bf-->e838b1325db49254e54c0709041c472a",
      "title": "<table class=\"table\">\n<tr><th>2</th><td>KeyEvent(state=b49ae4a12aec1025e366bba30c1075bf, name=BACK)</td></tr>\n<tr><th>3</th><td>IntentEvent(intent='am force-stop com.example.chatter')</td></tr>\n</table>",
      "label": "2, 3",
      "events": [
        {
          "event_str": "KeyEvent(state=b49ae4a12aec1025e366bba30c1075bf, name=BACK)",
          "event_id": 2,
          "event_type": "key",
          "view_images": []
        },
        {
          "event_str": "IntentEvent(intent='am force-stop com.example.chatter')",
          "event_id": 3,
          "event_type": "intent",
          "view_images": []
        }
      ]
    }
  ],
  "num_nodes": 2,
  "num_edges": 2,
  "num_effective_events": 3,
  "num_reached_activities": 1,
  "test_date": "2025-01-25 15:42:27",
  "time_spent": 85.864363,
  "num_transitions": 20,
  "device_serial": "061222511D012222",
  "device_model_number": "Infinix X683",
  "device_sdk_version": 29,
  "app_sha256": "96449287923729ce4eeced4f18527f874f21914aa7798beb239d5747b8f442bd",
  "app_package": "com.example.chatter",
  "app_main_activity": "com.example.chatter.Splash",
  "app_num_total_activities": 11
}