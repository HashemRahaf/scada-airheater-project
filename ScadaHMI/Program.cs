using System;
using System.Data;
using System.Drawing;
using System.Windows.Forms;
using Microsoft.Data.SqlClient;

namespace ScadaHMI
{
    internal static class Program
    {
        [STAThread]
        static void Main()
        {
            ApplicationConfiguration.Initialize();
            Application.Run(new MainForm());
        }
    }

    public class MainForm : Form
    {
        // Change this if your SQL Server name is different.
        private readonly string connStr =
            "Server=ZEM-RAHAF\\SQLEXPRESS;" +
            "Database=SCADA_AirHeater;" +
            "Trusted_Connection=True;" +
            "TrustServerCertificate=True;";

        private Panel headerPanel;
        private Panel buttonPanel;
        private Panel livePanel;
        private Panel alarmPanel;
        private Panel statusPanel;

        private Label lblTitle;
        private Label lblSubtitle;
        private Label lblLiveTitle;
        private Label lblAlarmTitle;
        private Label lblStatus;

        private Button btnHome;
        private Button btnRefresh;
        private Button btnAcknowledge;
        private Button btnExit;

        private DataGridView gridLive;
        private DataGridView gridAlarms;

        private System.Windows.Forms.Timer timerLive;

        public MainForm()
        {
            BuildUserInterface();
            Load += MainForm_Load;
        }

        private void BuildUserInterface()
        {
            Text = "SCADA Air Heater HMI";
            Width = 1250;
            Height = 760;
            MinimumSize = new Size(1100, 680);
            StartPosition = FormStartPosition.CenterScreen;
            BackColor = Color.FromArgb(245, 247, 250);

            // =========================
            // Header
            // =========================
            headerPanel = new Panel();
            headerPanel.Dock = DockStyle.Top;
            headerPanel.Height = 90;
            headerPanel.BackColor = Color.FromArgb(25, 42, 86);

            lblTitle = new Label();
            lblTitle.Text = "SCADA Air Heater HMI";
            lblTitle.ForeColor = Color.White;
            lblTitle.Font = new Font("Segoe UI", 20, FontStyle.Bold);
            lblTitle.AutoSize = true;
            lblTitle.Location = new Point(25, 15);

            lblSubtitle = new Label();
            lblSubtitle.Text = "Simulated air-heater control, datalogging and alarm monitoring";
            lblSubtitle.ForeColor = Color.FromArgb(220, 225, 235);
            lblSubtitle.Font = new Font("Segoe UI", 10, FontStyle.Regular);
            lblSubtitle.AutoSize = true;
            lblSubtitle.Location = new Point(29, 58);

            headerPanel.Controls.Add(lblTitle);
            headerPanel.Controls.Add(lblSubtitle);

            // =========================
            // Button Panel
            // =========================
            buttonPanel = new Panel();
            buttonPanel.Dock = DockStyle.Top;
            buttonPanel.Height = 65;
            buttonPanel.BackColor = Color.White;
            buttonPanel.Padding = new Padding(20, 12, 20, 10);

            btnHome = CreateButton("Home / Overview", Color.FromArgb(52, 152, 219));
            btnRefresh = CreateButton("Refresh", Color.FromArgb(46, 204, 113));
            btnAcknowledge = CreateButton("Acknowledge Alarm", Color.FromArgb(243, 156, 18));
            btnExit = CreateButton("Exit", Color.FromArgb(231, 76, 60));

            btnHome.Location = new Point(25, 13);
            btnRefresh.Location = new Point(190, 13);
            btnAcknowledge.Location = new Point(335, 13);
            btnExit.Location = new Point(555, 13);

            btnHome.Width = 145;
            btnRefresh.Width = 125;
            btnAcknowledge.Width = 190;
            btnExit.Width = 100;

            btnHome.Click += BtnHome_Click;
            btnRefresh.Click += BtnRefresh_Click;
            btnAcknowledge.Click += BtnAcknowledge_Click;
            btnExit.Click += BtnExit_Click;

            buttonPanel.Controls.Add(btnHome);
            buttonPanel.Controls.Add(btnRefresh);
            buttonPanel.Controls.Add(btnAcknowledge);
            buttonPanel.Controls.Add(btnExit);

            // =========================
            // Live Process Values Panel
            // =========================
            livePanel = new Panel();
            livePanel.Dock = DockStyle.Top;
            livePanel.Height = 265;
            livePanel.BackColor = Color.White;
            livePanel.Padding = new Padding(20, 10, 20, 10);
            livePanel.Margin = new Padding(20);

            lblLiveTitle = new Label();
            lblLiveTitle.Text = "Live Process Values";
            lblLiveTitle.Font = new Font("Segoe UI", 13, FontStyle.Bold);
            lblLiveTitle.ForeColor = Color.FromArgb(40, 40, 40);
            lblLiveTitle.AutoSize = true;
            lblLiveTitle.Location = new Point(20, 10);

            gridLive = new DataGridView();
            gridLive.Location = new Point(20, 45);
            gridLive.Width = 1190;
            gridLive.Height = 195;
            gridLive.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right | AnchorStyles.Bottom;
            gridLive.ReadOnly = true;
            gridLive.AllowUserToAddRows = false;
            gridLive.AllowUserToDeleteRows = false;
            gridLive.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            gridLive.MultiSelect = false;
            gridLive.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.None;

            livePanel.Controls.Add(lblLiveTitle);
            livePanel.Controls.Add(gridLive);

            // =========================
            // Alarm Panel
            // =========================
            alarmPanel = new Panel();
            alarmPanel.Dock = DockStyle.Fill;
            alarmPanel.BackColor = Color.White;
            alarmPanel.Padding = new Padding(20, 10, 20, 10);

            lblAlarmTitle = new Label();
            lblAlarmTitle.Text = "Active Alarms";
            lblAlarmTitle.Font = new Font("Segoe UI", 13, FontStyle.Bold);
            lblAlarmTitle.ForeColor = Color.FromArgb(40, 40, 40);
            lblAlarmTitle.AutoSize = true;
            lblAlarmTitle.Location = new Point(20, 10);

            gridAlarms = new DataGridView();
            gridAlarms.Location = new Point(20, 45);
            gridAlarms.Width = 1190;
            gridAlarms.Height = 230;
            gridAlarms.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right | AnchorStyles.Bottom;
            gridAlarms.ReadOnly = true;
            gridAlarms.AllowUserToAddRows = false;
            gridAlarms.AllowUserToDeleteRows = false;
            gridAlarms.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            gridAlarms.MultiSelect = false;
            gridAlarms.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.None;

            alarmPanel.Controls.Add(lblAlarmTitle);
            alarmPanel.Controls.Add(gridAlarms);

            // =========================
            // Status Panel
            // =========================
            statusPanel = new Panel();
            statusPanel.Dock = DockStyle.Bottom;
            statusPanel.Height = 32;
            statusPanel.BackColor = Color.FromArgb(236, 240, 241);

            lblStatus = new Label();
            lblStatus.Text = "Status: Ready";
            lblStatus.Font = new Font("Segoe UI", 9, FontStyle.Italic);
            lblStatus.ForeColor = Color.FromArgb(60, 60, 60);
            lblStatus.AutoSize = true;
            lblStatus.Location = new Point(20, 8);

            statusPanel.Controls.Add(lblStatus);

            // =========================
            // Timer
            // =========================
            timerLive = new System.Windows.Forms.Timer();
            timerLive.Interval = 2000;
            timerLive.Tick += TimerLive_Tick;

            // Add panels to form
            Controls.Add(alarmPanel);
            Controls.Add(livePanel);
            Controls.Add(buttonPanel);
            Controls.Add(headerPanel);
            Controls.Add(statusPanel);
        }

        private Button CreateButton(string text, Color color)
        {
            Button button = new Button();
            button.Text = text;
            button.Height = 38;
            button.FlatStyle = FlatStyle.Flat;
            button.FlatAppearance.BorderSize = 0;
            button.BackColor = color;
            button.ForeColor = Color.White;
            button.Font = new Font("Segoe UI", 9, FontStyle.Bold);
            button.Cursor = Cursors.Hand;
            return button;
        }

        private void MainForm_Load(object? sender, EventArgs e)
        {
            RefreshLiveValues();
            RefreshAlarms();
            timerLive.Start();
        }

        private void TimerLive_Tick(object? sender, EventArgs e)
        {
            RefreshLiveValues();
            RefreshAlarms();
        }

        private void BtnHome_Click(object? sender, EventArgs e)
        {
            RefreshLiveValues();
            RefreshAlarms();

            MessageBox.Show(
                "SCADA overview refreshed.\n\nThe HMI shows live process values and active alarms from SQL Server.",
                "Home / Overview",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
        }

        private void BtnRefresh_Click(object? sender, EventArgs e)
        {
            RefreshLiveValues();
            RefreshAlarms();
        }

        private void BtnExit_Click(object? sender, EventArgs e)
        {
            DialogResult result = MessageBox.Show(
                "Do you want to close the SCADA HMI?",
                "Exit",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Question
            );

            if (result == DialogResult.Yes)
            {
                Close();
            }
        }

        private void RefreshLiveValues()
        {
            try
            {
                using SqlConnection conn = new SqlConnection(connStr);
                using SqlCommand cmd = new SqlCommand("dbo.GetLatestValues", conn);

                cmd.CommandType = CommandType.StoredProcedure;

                DataTable dt = new DataTable();

                conn.Open();
                dt.Load(cmd.ExecuteReader());

                gridLive.DataSource = dt;

                FormatGrid(gridLive);
                FormatLiveGridColumns();
                ColorLiveRows();

                lblStatus.Text = "Status: Live values updated at " +
                                 DateTime.Now.ToString("HH:mm:ss");
            }
            catch (Exception ex)
            {
                timerLive.Stop();

                MessageBox.Show(
                    "Error while loading live process values:\n\n" + ex.Message,
                    "Database Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );

                lblStatus.Text = "Status: Database error while loading live values.";
            }
        }

        private void RefreshAlarms()
        {
            try
            {
                string sql = @"
                    SELECT 
                        AlarmEventID,
                        AlarmName,
                        Priority,
                        StartTimeUTC,
                        AlarmValue,
                        Unit,
                        Status,
                        Acknowledged,
                        AcknowledgedBy,
                        AcknowledgedTimeUTC
                    FROM dbo.vw_ActiveAlarms
                    ORDER BY StartTimeUTC DESC;
                ";

                using SqlConnection conn = new SqlConnection(connStr);
                using SqlCommand cmd = new SqlCommand(sql, conn);

                DataTable dt = new DataTable();

                conn.Open();
                dt.Load(cmd.ExecuteReader());

                gridAlarms.DataSource = dt;

                FormatGrid(gridAlarms);
                FormatAlarmGridColumns();
                ColorAlarmRows();
            }
            catch (Exception ex)
            {
                timerLive.Stop();

                MessageBox.Show(
                    "Error while loading alarms:\n\n" + ex.Message,
                    "Database Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );

                lblStatus.Text = "Status: Database error while loading alarms.";
            }
        }

        private void BtnAcknowledge_Click(object? sender, EventArgs e)
        {
            if (gridAlarms.CurrentRow == null)
            {
                MessageBox.Show(
                    "Select an alarm row first.",
                    "Acknowledge Alarm",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Warning
                );
                return;
            }

            if (!gridAlarms.Columns.Contains("AlarmEventID"))
            {
                MessageBox.Show(
                    "AlarmEventID column was not found.",
                    "Acknowledge Alarm",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
                return;
            }

            object? alarmIdObject = gridAlarms.CurrentRow.Cells["AlarmEventID"].Value;

            if (alarmIdObject == null || alarmIdObject == DBNull.Value)
            {
                MessageBox.Show(
                    "No valid alarm selected.",
                    "Acknowledge Alarm",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Warning
                );
                return;
            }

            long alarmEventId = Convert.ToInt64(alarmIdObject);

            DialogResult confirm = MessageBox.Show(
                "Acknowledge selected alarm?",
                "Acknowledge Alarm",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Question
            );

            if (confirm != DialogResult.Yes)
            {
                return;
            }

            try
            {
                using SqlConnection conn = new SqlConnection(connStr);
                using SqlCommand cmd = new SqlCommand("dbo.AcknowledgeAlarm", conn);

                cmd.CommandType = CommandType.StoredProcedure;
                cmd.Parameters.AddWithValue("@AlarmEventID", alarmEventId);
                cmd.Parameters.AddWithValue("@AcknowledgedBy", "Rahaf");

                conn.Open();
                cmd.ExecuteNonQuery();

                RefreshAlarms();

                lblStatus.Text = "Status: Alarm " + alarmEventId +
                                 " acknowledged at " + DateTime.Now.ToString("HH:mm:ss");

                MessageBox.Show(
                    "Alarm acknowledged successfully.",
                    "SCADA HMI",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information
                );
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    "Error while acknowledging alarm:\n\n" + ex.Message,
                    "Database Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );

                lblStatus.Text = "Status: Error while acknowledging alarm.";
            }
        }

        private void FormatGrid(DataGridView grid)
        {
            grid.RowHeadersVisible = false;
            grid.BackgroundColor = Color.White;
            grid.BorderStyle = BorderStyle.FixedSingle;
            grid.GridColor = Color.FromArgb(220, 220, 220);

            grid.ColumnHeadersDefaultCellStyle.Font =
                new Font("Segoe UI", 9, FontStyle.Bold);

            grid.ColumnHeadersDefaultCellStyle.BackColor =
                Color.FromArgb(210, 225, 245);

            grid.ColumnHeadersDefaultCellStyle.ForeColor = Color.Black;

            grid.DefaultCellStyle.Font =
                new Font("Segoe UI", 9, FontStyle.Regular);

            grid.DefaultCellStyle.SelectionBackColor =
                Color.FromArgb(41, 128, 185);

            grid.DefaultCellStyle.SelectionForeColor = Color.White;

            grid.EnableHeadersVisualStyles = false;
            grid.AllowUserToResizeRows = false;
        }

        private void FormatLiveGridColumns()
        {
            if (gridLive.Columns.Count == 0)
                return;

            if (gridLive.Columns.Contains("TagName"))
                gridLive.Columns["TagName"].Width = 250;

            if (gridLive.Columns.Contains("Description"))
                gridLive.Columns["Description"].Width = 350;

            if (gridLive.Columns.Contains("Unit"))
                gridLive.Columns["Unit"].Width = 80;

            if (gridLive.Columns.Contains("TimestampUTC"))
                gridLive.Columns["TimestampUTC"].Width = 180;

            if (gridLive.Columns.Contains("Value"))
            {
                gridLive.Columns["Value"].Width = 120;
                gridLive.Columns["Value"].DefaultCellStyle.Format = "N2";
            }

            if (gridLive.Columns.Contains("QualityFlag"))
                gridLive.Columns["QualityFlag"].Width = 130;
        }

        private void FormatAlarmGridColumns()
        {
            if (gridAlarms.Columns.Count == 0)
                return;

            if (gridAlarms.Columns.Contains("AlarmEventID"))
                gridAlarms.Columns["AlarmEventID"].Width = 90;

            if (gridAlarms.Columns.Contains("AlarmName"))
                gridAlarms.Columns["AlarmName"].Width = 240;

            if (gridAlarms.Columns.Contains("Priority"))
                gridAlarms.Columns["Priority"].Width = 90;

            if (gridAlarms.Columns.Contains("StartTimeUTC"))
                gridAlarms.Columns["StartTimeUTC"].Width = 170;

            if (gridAlarms.Columns.Contains("AlarmValue"))
            {
                gridAlarms.Columns["AlarmValue"].Width = 115;
                gridAlarms.Columns["AlarmValue"].DefaultCellStyle.Format = "N2";
            }

            if (gridAlarms.Columns.Contains("Unit"))
                gridAlarms.Columns["Unit"].Width = 70;

            if (gridAlarms.Columns.Contains("Status"))
                gridAlarms.Columns["Status"].Width = 95;

            if (gridAlarms.Columns.Contains("Acknowledged"))
                gridAlarms.Columns["Acknowledged"].Width = 115;

            if (gridAlarms.Columns.Contains("AcknowledgedBy"))
                gridAlarms.Columns["AcknowledgedBy"].Width = 140;

            if (gridAlarms.Columns.Contains("AcknowledgedTimeUTC"))
                gridAlarms.Columns["AcknowledgedTimeUTC"].Width = 180;
        }

        private void ColorLiveRows()
        {
            foreach (DataGridViewRow row in gridLive.Rows)
            {
                row.DefaultCellStyle.BackColor = Color.FromArgb(235, 247, 255);
            }
        }

        private void ColorAlarmRows()
        {
            foreach (DataGridViewRow row in gridAlarms.Rows)
            {
                string priority = "";

                if (gridAlarms.Columns.Contains("Priority") &&
                    row.Cells["Priority"].Value != null)
                {
                    priority = row.Cells["Priority"].Value.ToString() ?? "";
                }

                if (priority.Equals("High", StringComparison.OrdinalIgnoreCase))
                {
                    row.DefaultCellStyle.BackColor = Color.FromArgb(255, 225, 225);
                }
                else if (priority.Equals("Medium", StringComparison.OrdinalIgnoreCase))
                {
                    row.DefaultCellStyle.BackColor = Color.FromArgb(255, 246, 210);
                }
                else
                {
                    row.DefaultCellStyle.BackColor = Color.White;
                }
            }
        }
    }
}
