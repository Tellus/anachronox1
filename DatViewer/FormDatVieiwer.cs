using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.IO;

namespace DatViewer
{
    public partial class FormDatVieiwer : Form
    {
        DatSupport.DatArchive Archive;

        public FormDatVieiwer()
        {
            InitializeComponent();
        }

        private void FormDatVieiwer_Load(object sender, EventArgs e)
        {
            doOpenFileAction();
        }

        protected void doOpenFileAction()
        {
            DatOpenFileDialog.ShowDialog(this);

            if (Archive != null) Archive.Dispose();
            Archive = new DatSupport.DatArchive(DatOpenFileDialog.FileName);

            // Do a swift refresh.
            RefreshTreeview();
        }

        /// <summary>
        /// Refreshes the contents of the DAT file treeview based on the DatArchive currently open.
        /// </summary>
        public void RefreshTreeview()
        {
            // Empty out, y'all!
            DatTreeView.Nodes.Clear();
            // Base node. Makes my algorithms easier to design.
            DatTreeView.Nodes.Add("<root>");

            // Think we need something recursive here.
            foreach (DatSupport.DatFileInfo file in Archive.Files)
            {
                addFileToNode(file);
            }
        }

        protected void addFileToNode(DatSupport.DatFileInfo file)
        {
            List<String> dirPath = file.GetDirectoryPath();

            TreeNode baseNode = DatTreeView.Nodes[0]; // <root> node.
            TreeNode tmpNode;
            foreach (string s in dirPath)
            {
                // We might have to make this finde work through children. It does, however, bear the risk of dir structure corruption.
                if (!baseNode.Nodes.ContainsKey(s))
                {
                    tmpNode = baseNode.Nodes.Add(s, s);
                }
                else
                {
                    tmpNode = baseNode.Nodes.Find(s, false)[0];
                }
                baseNode = tmpNode;
            }

            // Finally, add the file itself.
            int lIndex = file.FileName.LastIndexOf(@"\");
            string fileName = file.FileName.Substring(lIndex == -1 ? 0 : lIndex + 1);
            TreeNode newNode = baseNode.Nodes.Add(fileName, fileName);
            newNode.Tag = file.FileName; // Tag the full name. Better style would be to make a small subclass of TreeNode.
        }

        private void OpenDatButton_Click(object sender, EventArgs e)
        {
            doOpenFileAction();
        }

        private void ExtractSingleButton_Click(object sender, EventArgs e)
        {
            DatSingleSaveDialog.ShowDialog(this);
            Archive.ExtractFile((string)DatTreeView.SelectedNode.Tag, DatSingleSaveDialog.FileName).Close();
        }

        private void ExtractAllButton_Click(object sender, EventArgs e)
        {
            DatSaveAllDialog.ShowDialog(this);
            Archive.ExtractAll(DatSaveAllDialog.FileName);
        }
    }
}
