import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.2
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.kirigami 2.8 as Kirigami
import Mycroft 1.0 as Mycroft

Item {
    id: contactsPage
    anchors.fill: parent
    
    RowLayout {
        id: contactsPageHeading
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        
        Image {
            id: backButton
            Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
            Layout.leftMargin: Kirigami.Units.largeSpacing
            Layout.preferredWidth: Kirigami.Units.iconSizes.medium
            Layout.preferredHeight: Kirigami.Units.iconSizes.medium
            source: "images/back.png"
            MouseArea {
                anchors.fill: parent
                onClicked: Mycroft.MycroftController.sendRequest("mycroft.mark2.reset_idle", {})
            }
        }
        
        Kirigami.Heading {
            level: 1
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            font.bold: true
            text: i18n("Contacts")
            color: Kirigami.Theme.highlightColor
        }
    }
        
    Kirigami.Separator {
        id: headerSept
        anchors.top: contactsPageHeading.bottom
        anchors.topMargin: Kirigami.Units.largeSpacing
        width: parent.width
        height: 1
    }
                    
    ListView {
        id: contactsView
        anchors.top: headerSept.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.topMargin: Kirigami.Units.largeSpacing
        anchors.bottomMargin: Kirigami.Units.gridUnit
        model: voipLoaderView.contactListModel
        clip: true
        delegate: ContactDelegate{}
    }
}
