using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

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
            DatOpenFileDialog.ShowDialog(this);

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
            TreeNode[] foundNodes;
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
            baseNode.Nodes.Add(fileName, fileName);
        }
    }
}
