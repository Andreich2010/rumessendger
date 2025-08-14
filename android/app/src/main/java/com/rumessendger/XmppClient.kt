package com.rumessendger

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.jivesoftware.smack.AbstractXMPPConnection
import org.jivesoftware.smack.chat2.ChatManager
import org.jivesoftware.smack.chat2.IncomingChatMessageListener
import org.jivesoftware.smack.packet.Message
import org.jivesoftware.smack.tcp.XMPPTCPConnection
import org.jivesoftware.smack.tcp.XMPPTCPConnectionConfiguration
import org.jivesoftware.smackx.omemo.OmemoManager
import org.jivesoftware.smackx.pushnotifications.PushNotificationsManager
import org.jxmpp.jid.EntityBareJid
import org.jxmpp.jid.impl.JidCreate

/**
 * Simple XMPP client using Smack that connects to the configured ejabberd
 * server, sends messages and registers for push notifications.
 */
object XmppClient {
    private var connection: AbstractXMPPConnection? = null

    suspend fun connect() = withContext(Dispatchers.IO) {
        val config = XMPPTCPConnectionConfiguration.builder()
            .setXmppDomain(XmppConfig.DOMAIN)
            .setHost(XmppConfig.HOST)
            .setResource(XmppConfig.RESOURCE)
            .build()
        connection = XMPPTCPConnection(config).apply {
            connect()
            login(XmppConfig.USERNAME, XmppConfig.PASSWORD)
        }
    }

    fun sendMessage(to: String, body: String) {
        val jid = JidCreate.entityBareFrom(to)
        ChatManager.getInstanceFor(connection).chatWith(jid).send(body)
    }

    fun addIncomingListener(listener: (EntityBareJid, Message) -> Unit) {
        ChatManager.getInstanceFor(connection)
            .addIncomingListener(IncomingChatMessageListener { from, message, _ ->
                listener(from, message)
            })
    }

    fun enableOmemo() {
        connection?.let { OmemoManager.getInstanceFor(it).initialize() }
    }

    fun registerPush(token: String) {
        val pushManager = PushNotificationsManager.getInstanceFor(connection)
        val jid = JidCreate.entityFullFrom("${XmppConfig.USERNAME}@${XmppConfig.DOMAIN}/${XmppConfig.RESOURCE}")
        val pubSub = JidCreate.domainFullFrom("push.${XmppConfig.DOMAIN}")
        pushManager.enable(jid, pubSub, token)
    }
}
