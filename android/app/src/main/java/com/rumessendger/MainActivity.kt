package com.rumessendger

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import org.jivesoftware.smack.packet.Message
import org.jxmpp.jid.EntityBareJid

/**
 * Minimal activity demonstrating connection and message handling.
 */
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            XmppClient.connect()
            XmppClient.setEncryption(XmppClient.EncryptionMode.STANDARD)
            XmppClient.fetchMamHistory(null)
            XmppClient.addIncomingListener(::onIncomingMessage)
        }
    }

    private fun onIncomingMessage(from: EntityBareJid, message: Message) {
        // Handle incoming messages here
    }
}
