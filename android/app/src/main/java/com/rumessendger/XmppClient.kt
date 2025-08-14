package com.rumessendger

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.jivesoftware.smack.AbstractXMPPConnection
import org.jivesoftware.smack.ReconnectionManager
import org.jivesoftware.smack.chat2.ChatManager
import org.jivesoftware.smack.chat2.IncomingChatMessageListener
import org.jivesoftware.smack.packet.Message
import org.jivesoftware.smack.tcp.XMPPTCPConnection
import org.jivesoftware.smack.tcp.XMPPTCPConnectionConfiguration
import org.jivesoftware.smackx.mam.MamManager
import org.jivesoftware.smackx.omemo.OmemoManager
import org.jivesoftware.smackx.pushnotifications.PushNotificationsManager
import org.jxmpp.jid.EntityBareJid
import org.jxmpp.jid.impl.JidCreate

/**
 * Simple XMPP client using Smack that connects to the configured ejabberd
 * server, sends messages and registers for push notifications.
 */
object XmppClient {
    enum class EncryptionMode { STANDARD, PERSONAL }

    private var connection: AbstractXMPPConnection? = null
    private var encryptionMode: EncryptionMode = EncryptionMode.STANDARD

    suspend fun connect() = withContext(Dispatchers.IO) {
        val config = XMPPTCPConnectionConfiguration.builder()
            .setXmppDomain(XmppConfig.DOMAIN)
            .setHost(XmppConfig.HOST)
            .setResource(XmppConfig.RESOURCE)
            .setUseStreamManagement(true)
            .setUseStreamManagementResumption(true)
            .build()
        connection = XMPPTCPConnection(config).apply {
            ReconnectionManager.getInstanceFor(this).enableAutomaticReconnection()
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

    fun setEncryption(mode: EncryptionMode) {
        encryptionMode = mode
        if (mode == EncryptionMode.PERSONAL) {
            connection?.let { OmemoManager.getInstanceFor(it).initialize() }
        }
    }

    suspend fun fetchMamHistory(afterUid: String? = null) = withContext(Dispatchers.IO) {
        val conn = connection ?: return@withContext
        val mam = MamManager.getInstanceFor(conn)
        val args = MamManager.MamQueryArgs.Builder().also { builder ->
            if (afterUid != null) builder.setAfter(afterUid)
        }.build()
        mam.queryArchive(args)
    }

    fun registerPush(token: String) {
        val pushManager = PushNotificationsManager.getInstanceFor(connection)
        val jid = JidCreate.entityFullFrom("${XmppConfig.USERNAME}@${XmppConfig.DOMAIN}/${XmppConfig.RESOURCE}")
        val pubSub = JidCreate.domainFullFrom("push.${XmppConfig.DOMAIN}")
        pushManager.enable(jid, pubSub, token)
    }
}
