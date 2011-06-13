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
            this.OpenDatButton = new System.Windows.Forms.Button();
            this.ExtractSingleButton = new System.Windows.Forms.Button();
            this.ExtractAllButton = new System.Windows.Forms.Button();
            this.DatSingleSaveDialog = new System.Windows.Forms.SaveFileDialog();
            this.DatSaveAllDialog = new System.Windows.Forms.SaveFileDialog();
            this.SuspendLayout();
            // 
            // DatTreeView
            // 
            this.DatTreeView.Dock = System.Windows.Forms.DockStyle.Top;
            this.DatTreeView.Location = new System.Drawing.Point(0, 0);
            this.DatTreeView.Name = "DatTreeView";
            this.DatTreeView.Size = new System.Drawing.Size(402, 462);
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
            // OpenDatButton
            // 
            this.OpenDatButton.Location = new System.Drawing.Point(12, 468);
            this.OpenDatButton.Name = "OpenDatButton";
            this.OpenDatButton.Size = new System.Drawing.Size(119, 23);
            this.OpenDatButton.TabIndex = 1;
            this.OpenDatButton.Text = "Open DAT...";
            this.OpenDatButton.UseVisualStyleBackColor = true;
            this.OpenDatButton.Click += new System.EventHandler(this.OpenDatButton_Click);
            // 
            // ExtractSingleButton
            // 
            this.ExtractSingleButton.Location = new System.Drawing.Point(141, 468);
            this.ExtractSingleButton.Name = "ExtractSingleButton";
            this.ExtractSingleButton.Size = new System.Drawing.Size(119, 23);
            this.ExtractSingleButton.TabIndex = 2;
            this.ExtractSingleButton.Text = "Extract file...";
            this.ExtractSingleButton.UseVisualStyleBackColor = true;
            this.ExtractSingleButton.Click += new System.EventHandler(this.ExtractSingleButton_Click);
            // 
            // ExtractAllButton
            // 
            this.ExtractAllButton.Location = new System.Drawing.Point(271, 468);
            this.ExtractAllButton.Name = "ExtractAllButton";
            this.ExtractAllButton.Size = new System.Drawing.Size(119, 23);
            this.ExtractAllButton.TabIndex = 3;
            this.ExtractAllButton.Text = "Extract all...";
            this.ExtractAllButton.UseVisualStyleBackColor = true;
            this.ExtractAllButton.Click += new System.EventHandler(this.ExtractAllButton_Click);
            // 
            // DatSingleSaveDialog
            // 
            this.DatSingleSaveDialog.Filter = "All files|*.*";
            this.DatSingleSaveDialog.Title = "Save file as...";
            // 
            // DatSaveAllDialog
            // 
            this.DatSaveAllDialog.AddExtension = false;
            this.DatSaveAllDialog.Filter = "All files|*.*";
            this.DatSaveAllDialog.Title = "Extract all files to...";
            // 
            // FormDatVieiwer
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(402, 503);
            this.Controls.Add(this.ExtractAllButton);
            this.Controls.Add(this.ExtractSingleButton);
            this.Controls.Add(this.OpenDatButton);
            this.Controls.Add(this.DatTreeView);
            this.Name = "FormDatVieiwer";
            this.Text = "Anachronox Legacy DAT viewer.";
            this.Load += new System.EventHandler(this.FormDatVieiwer_Load);
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.TreeView DatTreeView;
        private System.Windows.Forms.OpenFileDialog DatOpenFileDialog;
        private System.Windows.Forms.Button OpenDatButton;
        private System.Windows.Forms.Button ExtractSingleButton;
        private System.Windows.Forms.Button ExtractAllButton;
        private System.Windows.Forms.SaveFileDialog DatSingleSaveDialog;
        private System.Windows.Forms.SaveFileDialog DatSaveAllDialog;
    }
}

