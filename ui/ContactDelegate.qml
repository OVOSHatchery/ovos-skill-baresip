import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.2
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.kirigami 2.4 as Kirigami
import Mycroft 1.0 as Mycroft

Kirigami.AbstractListItem {
    id: contactDelegate
    
    contentItem: Item {
        implicitWidth: delegateLayout.implicitWidth;
        implicitHeight: delegateLayout.implicitHeight;
        
        RowLayout {
            id: delegateLayout
            /*Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignVCenter
            */
            anchors {
                left: parent.left;
                top: parent.top;
                right: parent.right;
            }
            spacing: Math.round(units.gridUnit / 2)

            Image {
                id: contactIcon
                Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                Layout.preferredHeight: units.iconSizes.medium
                Layout.preferredWidth: units.iconSizes.medium
                source: "images/avatar.png"
            }

            Kirigami.Heading {
                id: contactNameLabel
                level: 2
                Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                color: Kirigami.Theme.textColor
                elide: Text.ElideRight
                text: name
                textFormat: Text.PlainText
            }
            
            Label {
                id: contactUrlLabel
                Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                color: Kirigami.Theme.textColor
                opacity: 0.8
                elide: Text.ElideRight
                text: url
                textFormat: Text.PlainText
            }
        }
    }
}
