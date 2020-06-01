import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.5 as Kirigami
import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    id: voipLoaderView
    
    property var pageToLoad: sessionData.pageState
    property var contactName: sessionData.currentContact
    property var callMuted: sessionData.call_muted
    property var contactListModel: sessionData.contactListModel
    
    onContactNameChanged: {
        console.log(contactName)
    }
    
    Loader {
        anchors.fill: parent
        id: rootLoader
    }

    onPageToLoadChanged: {
        console.log(sessionData.pageState)
        rootLoader.setSource(sessionData.pageState + ".qml")
    }
} 
