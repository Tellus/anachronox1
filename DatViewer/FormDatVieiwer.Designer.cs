namespace DatViewer
{
    partial class FormDatVieiwer
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.DatTreeView = new System.Windows.Forms.TreeView();
            this.DatOpenFileDialog = new System.Windows.Forms.OpenFileDialog();
            this.SuspendLayout();
            // 
            // DatTreeView
            // 
            this.DatTreeView.Dock = System.Windows.Forms.DockStyle.Fill;
            this.DatTreeView.Location = new System.Drawing.Point(0, 0);
            this.DatTreeView.Name = "DatTreeView";
            this.DatTreeView.Size = new System.Drawing.Size(600, 405);
            this.DatTreeView.TabIndex = 0;
            // 
            // DatOpenFileDialog
            // 
            this.DatOpenFileDialog.DefaultExt = "dat";
            this.DatOpenFileDialog.FileName = "openFileDialog1";
            this.DatOpenFileDialog.Filter = "Anachronox DAT file|*.dat";
            this.DatOpenFileDialog.ReadOnlyChecked = true;
            this.DatOpenFileDialog.Title = "Pick DAT file.";
            // 
            // FormDatVieiwer
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(600, 405);
            this.Controls.Add(this.DatTreeView);
            this.Name = "FormDatVieiwer";
            this.Text = "Anachronox Legacy DAT viewer.";
            this.Load += new System.EventHandler(this.FormDatVieiwer_Load);
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.TreeView DatTreeView;
        private System.Windows.Forms.OpenFileDialog DatOpenFileDialog;
    }
}

